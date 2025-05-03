import os
from dotenv import load_dotenv
import dspy
from dto import ReportRequest  
from account_schema_graphql import account_schema_graphql
from full_chema_graphql import full_schema


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

class ExtractReportRequestSignature(dspy.Signature):
    """Transforms natural language queries into structured object."""
    user_input = dspy.InputField(desc="Natural language query for fetching report data")
    graphQl_schema = dspy.InputField(desc="GraphQL schema definition")
    report_request: ReportRequest = dspy.OutputField(desc="Structured report request", type=ReportRequest)


class ReportRequestExtractor(dspy.Module):
    def __init__(self):
        super().__init__()
        self.extractor = dspy.ChainOfThought(ExtractReportRequestSignature)

    def forward(self, user_input, graphQl_schema):
        output = self.extractor(user_input=user_input, graphQl_schema=graphQl_schema)
        return dspy.Prediction(report_request=output.report_request)


# extractor = ReportRequestExtractor()

# # user_request = "get all accounts number and type along with customer name and age where customer name starts with 'v' and age is greater than 30"
# user_request = "get bill amount, duedate, number and month along with customer name and account type where amount is greater than 1000 and customer name starts with 'v' or account type is domestic"

# result = extractor(
#     user_input= user_request,
#     graphQl_schema= full_schema
# )
# print(result.report_request)