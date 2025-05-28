import os
from dotenv import load_dotenv
import dspy
from src.Examples.query_generator_examples import example_list
from graphql import build_schema, parse, validate

from src.dto import AndCondition, OrCondition, RelatedEntity, ReportRequest
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
        
        # self.generator.prompt_template = """
        # GraphQL Schema:
        # {graphql_schema}

        # User Request:
        # {request}

        # Generate a valid GraphQL query matching the schema and request. Return only the query.
        # """

    def forward(self, graphql_schema, request):
        result = self.generator(graphql_schema=graphql_schema, request=request)
        # dspy.Assert(is_valid_against_schema(result.query), "Generated GraphQL query has a syntax error.")
        return result


class QueryGenerationSignature(dspy.Signature):
    """Generate a GraphQL query based on schema and user request."""
    graphql_schema = dspy.InputField(desc="GraphQL schema definition")
    request: ReportRequest = dspy.InputField(desc="User request for data", type=ReportRequest)
    query : str = dspy.OutputField(desc="The GraphQL query only, with no explanation or surrounding text.")



# query_model = QueryGenerator()

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

# result = query_model(
#     graphql_schema= full_schema ,
#     request = report_request
# )

# print(result.query)