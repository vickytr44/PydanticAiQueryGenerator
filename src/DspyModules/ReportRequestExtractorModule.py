import os
from dotenv import load_dotenv
import dspy
import logfire
from src.Examples.report_generator_examples import extract_report_examples
from src.prompt import report_request_workflow_prompt
from src.dto import ReportRequest
from src.Schema.full_chema_graphql import full_schema
from dspy.teleprompt import BootstrapFewShot

logfire.configure(
    service_name="my_dspy_service",
    send_to_logfire=True,
)


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
    return prediction.report_request == example.report_request

class ExtractReportRequestSignature(dspy.Signature):
    """Transforms natural language queries into structured object."""
    user_input = dspy.InputField(desc="Natural language query for fetching report data")
    graphQl_schema = dspy.InputField(desc="GraphQL schema definition")
    report_request: ReportRequest = dspy.OutputField(desc="Structured report request", type=ReportRequest)


class ReportRequestExtractor(dspy.Module):
    def __init__(self):
        super().__init__()
        self.extractor = dspy.ChainOfThought(ExtractReportRequestSignature)

        #self.extractor.examples = extract_report_examples

        self.extractor.prompt_template = report_request_workflow_prompt


    def forward(self, user_input, graphQl_schema):
        with logfire.span("ReportRequestExtractor"):
            result = self.extractor(user_input=user_input, graphQl_schema=graphQl_schema)
            logfire.info(f"Report request extractor input: {user_input}, result: {result}")
            # Return the result of the analysis
            return result



if __name__ == "__main__":
    model = ReportRequestExtractor()

    tuner = BootstrapFewShot(metric=custom_exact_match, max_labeled_demos= 5, max_rounds=3)

    dataset = [dspy.Example(user_input=ex.input['user_input'], graphQl_schema = full_schema, report_request=ex.output).with_inputs("user_input","graphQl_schema") for ex in extract_report_examples]

    trained_model = tuner.compile(model, trainset= dataset)

    trained_model.save("C:\\PydanticAiReporting\\src\\optimized_programs\\report_request_extractor.pkl")


    # extractor = ReportRequestExtractor()

    # user_request = "get all accounts number and type along with customer name and age where customer name starts with 'v' and age is greater than 30"
    # user_request = "get bill amount, duedate, number and month along with customer name and account type where amount is greater than 1000 and customer name starts with 'v' or account type is domestic"
    # user_request = "what is the total unpaid bill amount of anna"
    # result = trained_model(
    #     user_input= user_request,
    #     graphQl_schema= full_schema
    # )
    # print(result.report_request)