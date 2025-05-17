import os
from dotenv import load_dotenv
import dspy
from dto import AndCondition, OrCondition, RelatedEntity, ReportRequest, SortCondition  
from Schema.account_schema_graphql import account_schema_graphql
from Schema.bill_schema_graphql import bill_schema_graphql
from Schema.full_chema_graphql import full_schema
from Examples.query_generator_examples import example_list

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
        return self.generator(graphql_schema=graphql_schema, request=request)


class QueryGenerationSignature(dspy.Signature):
    """Generate a GraphQL query based on schema and user request."""
    graphql_schema = dspy.InputField(desc="GraphQL schema definition")
    request: ReportRequest = dspy.InputField(desc="User request for data", type=ReportRequest)
    query : str = dspy.OutputField(desc="The GraphQL query only, with no explanation or surrounding text.")



# query_model = QueryGenerator()

# query_model.generator.examples = [few_shot_example1,few_shot_example2]

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
#     graphql_schema= bill_schema_graphql ,
#     request = report_request
# )

# print(result.query)