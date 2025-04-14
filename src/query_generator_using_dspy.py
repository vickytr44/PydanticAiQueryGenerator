import dspy
import os

from bill_schema_graphql import bill_schema_graphql

from dotenv import load_dotenv

from query_validator import validate_graphql_query

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

class QueryGenerationSignature(dspy.Signature):
    """Generate a GraphQL query based on schema and user request."""
    graphql_schema = dspy.InputField(desc="GraphQL schema definition")
    request = dspy.InputField(desc="User request for data")
    query = dspy.OutputField(desc="Generated GraphQL query")


query_generator_model = dspy.ChainOfThought(QueryGenerationSignature)

schema_str = bill_schema_graphql

user_request = """
    Fetch all bills where:
 
        - Any of the following must be true:
        - accounts.Type eq 'domestic'
        - customers.Name startsWith 'v'
 
        - And all of the following must be true:
        - bills.Amount gt '1000'
 
    Include the following fields:
    - **bills**: Number, Month, IsActive, Status, DueDate
        - **customers**: Name
        - **accounts**: Number, Type
        Sort results by:
        - **bills DueDate** in **descending** order
"""

result = query_generator_model(graphql_schema=schema_str, request=user_request)

validation_result = validate_graphql_query(result.query, schema_str)
print(validation_result, result.query)

