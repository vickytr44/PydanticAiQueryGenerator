from pydantic_ai import Agent, RunContext
from model import model
from prompt import orchestrator_agent_prompt
from strict_user_input_generator import user_input_agent, strict_user_input_result, Complete_request_result
from bill_schema_graphql import bill_schema_graphql
from query_generator import query_agent

from pydantic_ai.messages import (
    ModelMessage,
    ModelRequest,
    ModelResponse,
    TextPart,
    UserPromptPart,
)


orchestrator_agent = Agent(model, system_prompt=orchestrator_agent_prompt, model_settings={
    "temperature": 0.4, "timeout": 30
})

@orchestrator_agent.tool
def user_input_agent_tool(ctx: RunContext[str],user_input : str) -> list[str]:
    """
    Process user input using the user_input_agent to extract structured information.
    """
    result = user_input_agent.run_sync(user_input, usage=ctx.usage).data
    return result

@orchestrator_agent.tool_plain
def complete_request_generator_tool(deps : strict_user_input_result) -> str:
    """
    Generate a complete request string by combining user request and GraphQL schema.    
    """
    strict_user_input = deps.strict_user_input
    result = "\n### user request:\n" + strict_user_input + " " + "\n### GraphQL Schema:\n" + bill_schema_graphql
    return result

@orchestrator_agent.tool
def generate_query_tool(ctx: RunContext[None], deps: Complete_request_result) -> str:
    """
    Generate a GraphQL query based on completed request.
    """
    complete_request = deps.complete_request
    result = query_agent.run_sync(complete_request, usage=ctx.usage).data
    return result


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