import dspy
import os

from bill_schema_graphql import bill_schema_graphql

from dotenv import load_dotenv

from query_validator import validate_graphql_query

from dto import ReportRequest

load_dotenv(override=True)

model_name = os.getenv("MODEL_NAME")
azure_endpoint= os.getenv("AZURE_OPENAI_ENDPOINT")
api_key=os.getenv("AZURE_OPENAI_API_KEY")
version = os.getenv("OPENAI_API_VERSION")

# lm = dspy.LM(f'openai/{model_name}', api_key= api_key, api_base=azure_endpoint)
# dspy.configure(lm=lm)

lm = dspy.LM(
    model=f"azure/{model_name}",
    api_key=api_key,
    api_base=azure_endpoint,
    api_version=version
)

dspy.settings.configure(lm=lm, trace=["Test"])

class ExtractReportRequest(dspy.Signature):
    """Transforms natural language queries into structured report requests."""
    user_input = dspy.InputField(desc="Natural language query for fetching report data")
    report_request = dspy.OutputField(desc="Structured report request", type=ReportRequest)

extract_report_request = dspy.ChainOfThought(ExtractReportRequest)

class QueryGenerationSignature(dspy.Signature):
    """Generate a GraphQL query based on schema and user request."""
    graphql_schema = dspy.InputField(desc="GraphQL schema definition")
    request = dspy.InputField(desc="User request for data", type=ReportRequest)
    query = dspy.OutputField(desc="Generated GraphQL query")


query_generator_model = dspy.ChainOfThought(QueryGenerationSignature)


# schema_str = bill_schema_graphql

# user_request = ReportRequest(
#     main_entity="Account",
#     fields_to_fetch_from_main_entity="number, type",
#     and_conditions=["Customer.name starts with 'v'", "Customer.age > 30"],
#     or_conditions=None,
#     related_entity_fields={"Customer": "name, age"},
#     sort_field_order=None
# )

# result = query_generator_model(graphql_schema=schema_str, request=user_request)

# validation_result = validate_graphql_query(result.query, schema_str)
# print(validation_result, result.query)

# input="get all accounts number and type along with customer name and age where customer name starts with 'v' and age is greater than 30"
# result = extract_report_request(user_input=input)
# print(result.report_request)

