import os
from typing import List
from dotenv import load_dotenv
import dspy

from dto import ReportRequest


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
