import warnings
from gql import gql, Client
from gql.transport.requests import RequestsHTTPTransport

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
        gql_query = gql(query)
        response = client.execute(gql_query)
        print(response)
        # Check for 'errors' in the response and return if present
        if 'errors' in response:
            return {'errors': response['errors']}
        return response.get("data", response)  # Return only 'data' if present
    except Exception as e:
        return {"error": str(e)}  # Return error message if any



