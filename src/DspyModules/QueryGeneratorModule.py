import os
from dotenv import load_dotenv
import dspy
from src.Examples.query_generator_examples import example_list
from graphql import build_schema, parse, validate
from dspy.teleprompt import BootstrapFewShot

from src.dto import AndCondition, OrCondition, RelatedEntity, ReportRequest, SortCondition
from src.Schema.full_chema_graphql import full_schema

load_dotenv(override=True)

model_name = os.getenv("MODEL_NAME")
azure_endpoint= os.getenv("AZURE_OPENAI_ENDPOINT")
api_key=os.getenv("AZURE_OPENAI_API_KEY")
version = os.getenv("OPENAI_API_VERSION")

lm = dspy.LM(
    model=f"azure/{model_name}",
    api_key=api_key,
    api_base=azure_endpoint,
    api_version=version,
    temperature=0.3,
    top_p=0.95,
    cache= False,
    cache_in_memory=False,
)

dspy.settings.configure(lm=lm, trace=["Test"])

def custom_exact_match(example, prediction, trace=None):
    print("prediction",prediction, example)
    return prediction.query.strip() == example.query.strip()

def better_graphql_metric(example, prediction, trace=None):
    """
    A more sophisticated metric for GraphQL query evaluation
    """
    try:
        # Basic checks
        if not hasattr(prediction, 'query') or not prediction.query:
            return False
            
        predicted_query = prediction.query.strip()
        expected_query = example.query.strip()
        
        # 1. Exact match (best case)
        if predicted_query == expected_query:
            return True
            
        # 2. Normalize whitespace and compare
        import re
        def normalize_query(query):
            # Remove extra whitespace, normalize line breaks
            normalized = re.sub(r'\s+', ' ', query.replace('\n', ' ').replace('\t', ' '))
            return normalized.strip()
        
        if normalize_query(predicted_query) == normalize_query(expected_query):
            return True
            
        # 3. Check if both queries are syntactically valid GraphQL
        if is_valid_against_schema(predicted_query, full_schema) and \
           is_valid_against_schema(expected_query, full_schema):
            # Could add more semantic comparison here
            # For now, if both are valid, give partial credit
            return True
            
        return False
        
    except Exception as e:
        print(f"Error in metric evaluation: {e}")
        return False

def semantic_similarity_metric(example, prediction, trace=None):
    """
    Even more advanced metric using semantic similarity
    This would require additional libraries like sentence-transformers
    """
    # Basic validation first
    if not hasattr(prediction, 'query') or not prediction.query:
        return False
        
    # Check if both queries are syntactically valid
    predicted_valid = is_valid_against_schema(prediction.query.strip(), full_schema)
    expected_valid = is_valid_against_schema(example.query.strip(), full_schema)
    
    if not predicted_valid:
        return False
        
    # If both are valid, you could use semantic similarity
    # This is a simplified version - you'd want to use actual GraphQL AST comparison
    return predicted_valid and expected_valid

def is_valid_against_schema(query: str, schema_str: str) -> bool:
    try:
        schema = build_schema(schema_str)
        document = parse(query)
        errors = validate(schema, document)
        return not errors
    except Exception:
        return False

class QueryGenerator(dspy.Module):
    def __init__(self):
        super().__init__()

        self.generator = dspy.ChainOfThought(QueryGenerationSignature)

        self.generator.examples = example_list
        
        self.generator.prompt_template = """
        You are a GraphQL query generator. Follow this schema strictly.

        GraphQL Schema:
        {graphql_schema}

        Rules:
        1. Use the correct argument structure from the schema. Do NOT invent generic GraphQL patterns.
        2. Use `order: {{ fieldName: ASC|DESC }}` format if sorting is required.
        3. Do not use pagination (`first`, `limit`, etc.) unless explicitly asked.
        4. Only use fields and arguments defined in the schema.
        5. Return ONLY the query. No markdown, explanation, or comments.

        User Request:
        {request}

        Query:
        """

    def forward(self, graphql_schema, request):
        result = self.generator(graphql_schema=graphql_schema, request=request)
        # dspy.Suggest(is_valid_against_schema(result.query), "Generated GraphQL query has a syntax error.")
        return result


class QueryGenerationSignature(dspy.Signature):
    """Generate a GraphQL query based on schema and user request."""
    graphql_schema = dspy.InputField(desc="GraphQL schema definition")
    request: ReportRequest = dspy.InputField(desc="User request for data", type=ReportRequest)
    query : str = dspy.OutputField(desc="The GraphQL query only, with no explanation or surrounding text.")


if __name__ == "__main__":
    query_model = QueryGenerator()

    # Use the better metric instead of custom_exact_match
    tuner = BootstrapFewShot(metric=better_graphql_metric, max_labeled_demos= 5, max_rounds=3)

    dataset = [dspy.Example(graphql_schema = full_schema, request=ex.input['request'], query=ex.output).with_inputs("graphql_schema","request") for ex in example_list]

    print(f"Training with {len(dataset)} examples...")
    trained_query_generator = tuner.compile(query_model, trainset= dataset)

    trained_query_generator.save("C:\\PydanticAiReporting\\src\\optimized_programs\\query_generation_module.pkl")
    print("Training completed and model saved!")

    # query_model = QueryGenerator()    
    # query_model.load(path="C:\\PydanticAiReporting\\src\\optimized_programs\\query_generation_module.pkl")

    # report_request = ReportRequest(
    #     main_entity='Bill',
    #     fields_to_fetch_from_main_entity=['amount', 'dueDate', 'number', 'month'],
    #     or_conditions=[
    #         OrCondition(entity='Customer', field='name', operation='startsWith', value='v'),
    #         OrCondition(entity='Account', field='type', operation='eq', value='DOMESTIC')
    #     ],
    #     and_conditions=[
    #         AndCondition(entity='Bill', field='amount', operation='gt', value=500)
    #     ],
    #     related_entity_fields=[
    #         RelatedEntity(entity='Customer', fields=['name'])
    #     ],
    #     sort_field_order=None
    # )

    # report_request2 =ReportRequest(
    #     main_entity='Bill',
    #     fields_to_fetch_from_main_entity=['month', 'amount'],
    #     or_conditions=None,
    #     and_conditions=[
    #         AndCondition(entity='account', field='type', operation='eq', value='COMMERCIAL'),
    #         AndCondition(entity='account', field='customer.name', operation='eq', value='John')
    #     ],
    #     related_entity_fields=[
    #         RelatedEntity(entity='account', fields=['type', 'customer'])
    #     ],
    #     sort_field_order=None,
    #     include_count=False
    # )


    # result = query_model(
    #     graphql_schema= full_schema ,
    #     request = report_request2
    # )

    # print(result.query)
    
    # # Custom function to print the complete prompt including examples
    # def print_complete_prompt(n=1):
    #     from dspy.clients.base_lm import GLOBAL_HISTORY
        
    #     for item in GLOBAL_HISTORY[-n:]:
    #         messages = item["messages"] or [{"role": "user", "content": item["prompt"]}]
    #         timestamp = item.get("timestamp", "Unknown time")
            
    #         print(f"\n=== COMPLETE PROMPT [{timestamp}] ===\n")
            
    #         for msg in messages:
    #             print(f"--- {msg['role'].upper()} MESSAGE ---")
    #             if isinstance(msg["content"], str):
    #                 print(msg["content"].strip())
    #             else:
    #                 if isinstance(msg["content"], list):
    #                     for c in msg["content"]:
    #                         if c["type"] == "text":
    #                             print(c["text"].strip())
    #             print("\n" + "="*50 + "\n")
    
    # print_complete_prompt(n=1) 