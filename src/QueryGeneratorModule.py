import os
from dotenv import load_dotenv
import dspy
from dto import AndCondition, OrCondition, RelatedEntity, ReportRequest  
from account_schema_graphql import account_schema_graphql
from bill_schema_graphql import bill_schema_graphql

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
    temperature=0.4,
)

dspy.settings.configure(lm=lm, trace=["Test"])


class QueryGenerator(dspy.Module):
    def __init__(self):
        super().__init__()
        self.generator = dspy.ChainOfThought(QueryGenerationSignature)

    def forward(self, graphql_schema, request):
        output = self.generator(graphql_schema=graphql_schema, request=request)
        return dspy.Prediction(query=output.query)


class QueryGenerationSignature(dspy.Signature):
    """Generate a GraphQL query based on schema and user request."""
    graphql_schema = dspy.InputField(desc="GraphQL schema definition")
    request: ReportRequest = dspy.InputField(desc="User request for data", type=ReportRequest)
    query : str = dspy.OutputField(desc="The GraphQL query only, with no explanation or surrounding text.")


query_model = QueryGenerator()

report_request = ReportRequest(
    main_entity='Bill',
    fields_to_fetch_from_main_entity=['amount', 'dueDate', 'number', 'month'],
    or_conditions=[
        OrCondition(entity='Customer', field='name', operation='startsWith', value='v'),
        OrCondition(entity='Account', field='type', operation='eq', value='DOMESTIC')
    ],
    and_conditions=[
        AndCondition(entity='Bill', field='amount', operation='gt', value=1000)
    ],
    related_entity_fields=[
        RelatedEntity(entity='Customer', fields=['name', 'type'])
    ],
    sort_field_order=None
)

result = query_model(
    graphql_schema= bill_schema_graphql ,
    request = report_request
)

print(result.query)