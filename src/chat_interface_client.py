import asyncio
import os
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field
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

class ChatRequest(BaseModel):
    message: str = Field(
        description="The message to send to the AI assistant",
        example="Generate a report about sales data"
    )

class ChatResponse(BaseModel):
    response: str = Field(
        description="The AI assistant's response",
        example="I have generated a report based on the sales data..."
    )

app = FastAPI(
    title="AI Chat Interface API",
    description="API for interacting with the AI reporting system",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

@app.post("/chat", 
    response_model=ChatResponse,
    summary="Chat with AI Assistant",
    description="Send a message to the AI assistant and get a response. The assistant can generate GraphQL queries and reports based on your request."
)
async def chat_endpoint(request: ChatRequest):
    async with chat_interface_agent.run_mcp_servers():
        result = await chat_interface_agent.run(request.message, message_history=chat_history)
    chat_history.append(ModelRequest(parts=[UserPromptPart(content=request.message)]))
    chat_history.append(ModelResponse(parts=[TextPart(content=result.data)]))
    return {"response": result.data}

@app.get("/download/{report_id}")
def download_report(report_id: str):
    file_path = f"C:\\PydanticAiReporting\\FileStorage\\{report_id}.xlsx"
    if os.path.exists(file_path):
        return FileResponse(path=file_path, filename="report.xlsx", media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    else:
        raise HTTPException(status_code=404, detail="Report not found")

if __name__ == "__main__":
    import uvicorn
    # Run API server by default, use --cli flag to run in CLI mode
    import sys
    if "--cli" in sys.argv:
        asyncio.run(main())
    else:
        uvicorn.run(app, host="0.0.0.0", port=8080)