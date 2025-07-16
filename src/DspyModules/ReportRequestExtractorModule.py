import os
from dotenv import load_dotenv
import dspy
import logfire
from src.Examples.report_generator_examples import extract_report_examples
from src.prompt import report_request_workflow_prompt
from src.dto import ReportRequest
from src.Schema.full_chema_graphql import full_schema
from dspy.teleprompt import BootstrapFewShot
from src.token_utils import count_tokens

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

def normalize_conditions(conditions):
    """Converts list of condition objects to sorted tuples for comparison."""
    if conditions is None:
        return []
    return sorted([
        (c.entity.lower(), c.field.lower(), c.operation.lower(), str(c.value).lower())
        for c in conditions
    ])

def normalize_related_entities(related_fields):
    """Converts list of related entity objects to sorted tuples for comparison."""
    if related_fields is None:
        return []
    return sorted([
        (r.entity.lower(), tuple(sorted(f.lower() for f in r.fields)))
        for r in related_fields
    ])

def custom_exact_match(example, prediction, trace=None):
    a = example.report_request
    b = prediction.report_request

    return (
        a.main_entity.lower() == b.main_entity.lower() and
        sorted(f.lower() for f in (a.fields_to_fetch_from_main_entity or [])) ==
        sorted(f.lower() for f in (b.fields_to_fetch_from_main_entity or [])) and
        normalize_conditions(a.and_conditions) == normalize_conditions(b.and_conditions) and
        normalize_conditions(a.or_conditions) == normalize_conditions(b.or_conditions) and
        normalize_related_entities(a.related_entity_fields) == normalize_related_entities(b.related_entity_fields) and
        (a.sort_field_order or None) == (b.sort_field_order or None) and
        (a.include_count or False) == (b.include_count or False)
    )


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
        # Prepare messages for token counting
        messages = [
            {"role": "user", "content": user_input},
            {"role": "system", "content": str(graphQl_schema)}
        ]
        token_count = count_tokens(messages)
        logfire.info(f"Token count for LLM call: {token_count}")
        if token_count > 16000:
            logfire.warning(f"Token count for LLM call is very high: {token_count} (limit: 16385). Consider trimming input or schema.")
        with logfire.span("ReportRequestExtractor"):
            result = self.extractor(user_input=user_input, graphQl_schema=graphQl_schema)
            logfire.info(f"Report request extractor input: {user_input}, result: {result}, token_count: {token_count}")
            # Return the result of the analysis
            return result

if __name__ == "__main__":
    model = ReportRequestExtractor()

    tuner = BootstrapFewShot(metric=custom_exact_match, max_labeled_demos= 7, max_rounds=2)

    dataset = [dspy.Example(user_input=ex.input['user_input'], graphQl_schema = full_schema, report_request=ex.output).with_inputs("user_input","graphQl_schema") for ex in extract_report_examples]

    trained_model = tuner.compile(model, trainset= dataset)

    trained_model.save("C:\\PydanticAiReporting\\src\\optimized_programs\\report_request_extractor.pkl")


    # extractor = ReportRequestExtractor()

    # # user_request = "get all accounts number and type along with customer name and age where customer name starts with 'v' and age is greater than 30"
    # # user_request = "get bill amount, duedate, number and month along with customer name and account type where amount is greater than 1000 and customer name starts with 'v' or account type is domestic"
    # # user_request = "what is the total unpaid bill amount of anna"
    # user_request = "Generate a chart to visualize how bill amount varies from month to month for the commercial account of John."
    # result = extractor(
    #     user_input= user_request,
    #     graphQl_schema= full_schema
    # )
    # print(result.report_request)