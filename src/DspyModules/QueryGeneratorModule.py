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


query_model = QueryGenerator()

tuner = BootstrapFewShot(metric=custom_exact_match, max_labeled_demos= 5, max_rounds=3)

dataset = [dspy.Example(graphql_schema = full_schema, request=ex.input['request'], query=ex.output).with_inputs("graphql_schema","request") for ex in example_list]

trained_query_generator = tuner.compile(query_model, trainset= dataset)


# query_model = QueryGenerator()

# # report_request = ReportRequest(
# #     main_entity='Bill',
# #     fields_to_fetch_from_main_entity=['amount', 'dueDate', 'number', 'month'],
# #     or_conditions=[
# #         OrCondition(entity='Customer', field='name', operation='startsWith', value='v'),
# #         OrCondition(entity='Account', field='type', operation='eq', value='DOMESTIC')
# #     ],
# #     and_conditions=[
# #         AndCondition(entity='Bill', field='amount', operation='gt', value=500)
# #     ],
# #     related_entity_fields=[
# #         RelatedEntity(entity='Customer', fields=['name'])
# #     ],
# #     sort_field_order=None
# # )

# report_request2 =ReportRequest (
#     main_entity='Bill',
#     fields_to_fetch_from_main_entity=['amount'],
#     or_conditions=None,
#     and_conditions=None,
#     related_entity_fields=None,
#     sort_field_order=[
#         SortCondition(
#             entity='Bill',
#             field='amount',
#             order='DESC',
#         ),
#     ],
# )

# result = query_model(
#     graphql_schema= full_schema ,
#     request = report_request2
# )

# print(result.query)