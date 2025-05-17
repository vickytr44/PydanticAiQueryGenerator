import asyncio
from pydantic_ai import Agent
from pydantic_graph import Graph
from model import model
from pydantic_ai.mcp import MCPServerHTTP
from prompt import chat_interface_prompt

from workflow_graph import AssignEntitySchema, ExtractReportReuest, GenerateGraphQlQuery, ResolveError, State, validateGraphQlQuery, ExecuteGraphQlQuery, GenerateExcelReport

from pydantic_ai.messages import (
    ModelMessage,
    ModelRequest,
    ModelResponse,
    TextPart,
    UserPromptPart,
)

server = MCPServerHTTP(url="http://127.0.0.1:8000/sse")

chat_interface_agent = Agent(model, system_prompt= chat_interface_prompt, model_settings= {
    "temperature": 0.3, "timeout": 30, "top_p": 0.9
}, mcp_servers=[server])

@chat_interface_agent.tool_plain(name="Generate_GraphQl_Query_And_Report_Tool")
def Generate_GraphQl_Query_And_Report_Tool(input : str) -> str:
    """
    Generate a GraphQL query based on the user input and report by using the generated qery.
    """
    print("Generating GraphQL query...")
    state = State(input)
    query_generation_graph = Graph(nodes=(AssignEntitySchema, ExtractReportReuest, GenerateGraphQlQuery, validateGraphQlQuery, ResolveError, ExecuteGraphQlQuery, GenerateExcelReport))
    result = query_generation_graph.run_sync(AssignEntitySchema(), state=state)
    return result.output

chat_history : list[ModelMessage] = []  # Use a list to store messages 

async def main():
# Chat loop
    while True:
        query = input("You: ")
        if query.lower() == "exit":
            break
        chat_history.append(ModelRequest(parts=[UserPromptPart(content=query)]))  # Add user message

        async with chat_interface_agent.run_mcp_servers():  
            result = await chat_interface_agent.run(query, message_history=chat_history)

        chat_history.append(ModelResponse(parts=[TextPart(content=result.data)]))  # Add AI message

        print(f"AI: {result.data}")

if __name__ == "__main__":
    asyncio.run(main())