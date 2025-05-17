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


def execute_graphql_query(query: str):
    try:
        gql_query = gql(query)
        response = client.execute(gql_query)
        return response.get("data", response)  # Return only 'data' if present
    except Exception as e:
        return {"error": str(e)}  # Return error message if any



