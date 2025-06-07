from typing import List
from graphql import build_schema, parse, validate
from graphql.error import GraphQLError
from Schema.full_chema_graphql import full_schema

def validate_graphql_query(query: str, schema_str: str):
    try:
        # Build schema from schema string
        schema = build_schema(schema_str)

        # Parse the query to get the AST (Abstract Syntax Tree)
        parsed_query = parse(query)

        # Validate the query against the schema
        validation_errors = validate(schema, parsed_query)

        # Check if there were any validation errors
        if validation_errors:
            return ", ".join(error.message for error in validation_errors)
        else:
            return None

    except GraphQLError as e:
        return f"Error parsing or validating the query: {str(e)}"
    

def validate_graphql_query_for_workflow(query: str, schema_str: str) -> str | None:
    try:
        # Build schema from schema string
        schema = build_schema(schema_str)

        # Parse the query to get the AST (Abstract Syntax Tree)
        parsed_query = parse(query)

        # Validate the query against the schema
        validation_errors = validate(schema, parsed_query)

        # Check if there were any validation errors
        if validation_errors:
            return ", ".join(error.message for error in validation_errors)
        else:
            return None

    except GraphQLError as e:
        return [e.message]
    
if __name__ == "__main__":
    # Example usage
    query = """
            query {
                customers([order: { age: ASC }], where: { name: { startsWith: "v" } }) {
                    nodes {
                    age
                    id
                    identityNumber
                    name
                    }
                }
            }
    """
    #escaped_query = query.replace("{", "{{").replace("}", "}}")

    result = validate_graphql_query_for_workflow(query, full_schema)
    print(result)