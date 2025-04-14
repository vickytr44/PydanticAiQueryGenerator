from pydantic_ai import Agent, RunContext
from dto import ReportRequest
from model import model
from prompt import orchestrator_agent_dspy_prompt
from signature_definition_using_dspy import query_generator_model, extract_report_request
from bill_schema_graphql import bill_schema_graphql

from pydantic_ai.messages import (
    ModelMessage,
    ModelRequest,
    ModelResponse,
    TextPart,
    UserPromptPart,
)

orchestrator_agent = Agent(model, system_prompt=orchestrator_agent_dspy_prompt, model_settings={
    "temperature": 0.4, "timeout": 30
})

@orchestrator_agent.tool_plain
def extract_report_request_tool(input : str) -> ReportRequest:
    """
    Process user input to extract structured information.
    """
    print("Extracting report request...")
    result = extract_report_request(user_input= input)
    return result.report_request

@orchestrator_agent.tool_plain
def generate_query_tool(deps: ReportRequest) -> str:
    """
    Generate a GraphQL query based on the ReportRequest object.
    """
    result = query_generator_model(graphql_schema=bill_schema_graphql, request= deps)
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