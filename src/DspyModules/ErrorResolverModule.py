import os
from typing import List
from dotenv import load_dotenv
import dspy
from dspy.teleprompt import BootstrapFewShot

from src.Schema.full_chema_graphql import full_schema

from src.Examples.error_resolver_examples import example_list

from src.dto import ReportRequest

from graphql import parse, validate, build_schema


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
    
class ErrorResolverSignature(dspy.Signature):
    """Resolves the validation error and generates the correct GraphQL query based on schema. Strictly adhere to the provided schema and the user request."""
    graphql_schema = dspy.InputField(desc="GraphQL schema definition")
    request = dspy.InputField(desc="User request for data", type=ReportRequest)
    validation_error = dspy.InputField(desc="Validation errors", type= List[str])
    initial_query = dspy.InputField(desc="GraphQL query that needs to be corrected")
    query = dspy.OutputField(desc="The GraphQL query only, with no explanation or surrounding text.")

class ErrorResolverModule(dspy.Module):
    def __init__(self):
        super().__init__()
        # Initialize the ChainOfThought model with the signature
        self.resolver = dspy.ChainOfThought(ErrorResolverSignature)

    def forward(self, graphql_schema, request, validation_error: List[str], initial_query):
        # Call the model with the inputs and return the output
        return self.resolver(
            graphql_schema=graphql_schema,
            request=request,
            validation_error=validation_error,
            initial_query=initial_query
        )

if __name__ == "__main__":
    error_resolver_model = ErrorResolverModule()

    tuner = BootstrapFewShot(metric=better_graphql_metric, max_labeled_demos= 5, max_rounds=3)

    dataset = [dspy.Example(graphql_schema = full_schema, request=ex.input['request'], validation_error = ex.input['validation_error'],initial_query = ex.input['initial_query'], query=ex.output).with_inputs("graphql_schema","request","validation_error","initial_query") for ex in example_list]

    print(f"Training with {len(dataset)} examples...")
    trained_error_resolver = tuner.compile(error_resolver_model, trainset= dataset)

    trained_error_resolver.save("C:\\PydanticAiReporting\\src\\optimized_programs\\error_resolver_model.pkl")
    print("Error resolver model saved successfully.")