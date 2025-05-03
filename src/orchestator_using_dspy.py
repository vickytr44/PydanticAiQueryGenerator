from typing import List
from pydantic_ai import Agent, RunContext
from DspyModules.QueryGeneratorModule import QueryGenerator
from DspyModules.ReportRequestExtractorModule import ReportRequestExtractor
from dto import ReportRequest
from model import model
from prompt import orchestrator_agent_dspy_prompt
from query_validator import validate_graphql_query
from DspyModules.signature_definition_using_dspy import error_resolver_model
from Schema.full_chema_graphql import full_schema

from pydantic_ai.messages import (
    ModelMessage,
    ModelRequest,
    ModelResponse,
    TextPart,
    UserPromptPart,
)

orchestrator_agent = Agent(model, system_prompt=orchestrator_agent_dspy_prompt, model_settings={
    "temperature": 0.5, "timeout": 30
})

@orchestrator_agent.tool_plain
def extract_report_request_tool(input : str) -> ReportRequest:
    """
    Process user input to extract structured information.
    """
    print("Extracting report request...")
    extractor = ReportRequestExtractor()
    result = extractor(
        user_input= input,
        graphQl_schema= full_schema
    )
    return result.report_request

@orchestrator_agent.tool_plain
def generate_query_tool(report_request: ReportRequest) -> str:
    """
    Generate a GraphQL query based on the ReportRequest object.
    """
    print("generating query...", report_request)
    query_model = QueryGenerator()
    result = query_model(
        graphql_schema= full_schema ,
        request = report_request
    )
    return result.query

@orchestrator_agent.tool_plain
def validate_query_tool(graphQl_query: str) -> str | None:
    """
    validate the generated GraphQL query against the schema.
    """
    print("validating query...", graphQl_query)
    validation_error = validate_graphql_query(graphQl_query, full_schema)
    return validation_error

@orchestrator_agent.tool_plain
def error_resolver_tool(graphQl_query: str, validation_error: str, user_request: ReportRequest) -> str:
    """
    Resolve the validation errors and generate the correct graphQl query against the schema.
    """
    print("Resolving errors...", validation_error)
    result = error_resolver_model(graphql_schema=full_schema, request = user_request, validation_error = validation_error, initial_query= graphQl_query)
    return result.query


chat_history : list[ModelMessage] = []  # Use a list to store messages 

# Chat loop
while True:
    query = input("You: ")
    if query.lower() == "exit":
        break
    chat_history.append(ModelRequest(parts=[UserPromptPart(content=query)]))  # Add user message

    result = orchestrator_agent.run_sync(query, message_history=chat_history)

    chat_history.append(ModelResponse(parts=[TextPart(content=result.data)]))  # Add AI message

    print(f"AI: {result.data}")