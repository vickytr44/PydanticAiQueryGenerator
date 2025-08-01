import warnings
from gql import gql, Client
from gql.transport.requests import RequestsHTTPTransport
import logfire
logfire.configure()

# Define the GraphQL endpoint
transport = RequestsHTTPTransport(
    url="https://localhost:7075/graphql/",
    #headers={"Authorization": "Bearer YOUR_ACCESS_TOKEN"}  # Optional
    verify=False
)

warnings.simplefilter("ignore")

# Create a GraphQL client
client = Client(transport=transport, fetch_schema_from_transport=True)

def IsResponseEmpty(response_json: dict) -> bool:
    if not response_json:
        return True  # No data at all

    # Get the first entity (e.g., bills, accounts, etc.)
    entity = next(iter(response_json.values()), None)
    if not entity:
        return True  # No entity found

    nodes = entity.get("nodes")
    edges = entity.get("edges")
    total_count = entity.get("totalCount")

    # If totalCount is present, response is not empty
    if total_count is not None:
        return False

    # Case 1: Both keys are missing
    if nodes is None and edges is None:
        return True

    # Case 2: Both keys are present but empty
    if nodes == [] and edges == []:
        return True

    # Case 3: Only one key exists and is empty
    if nodes is not None and len(nodes) == 0 and edges is None:
        return True
    if edges is not None and len(edges) == 0 and nodes is None:
        return True

    # Case 4: At least one key has data
    return False


def execute_graphql_query(query: str):
    try:
        with logfire.span("perform_analysis"):  # Add tracing span            
            logfire.info(f"About to execute GraphQL query: {query}")  # <-- Add this
            gql_query = gql(query)
            response = client.execute(gql_query)
            logfire.info(f"Response for Executing GraphQL query: {query} is {response}")
            # Always log before any return
            if 'errors' in response:
                return {'errors': response['errors']}
            return response.get("data", response)  # Return only 'data' if present
    except Exception as e:
        logfire.error(f"Error executing GraphQL query: {e}")
        return {"error": str(e)}  # Return error message if any



