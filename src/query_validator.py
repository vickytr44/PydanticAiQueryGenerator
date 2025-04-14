from graphql import build_schema, parse, validate
from graphql.error import GraphQLError

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