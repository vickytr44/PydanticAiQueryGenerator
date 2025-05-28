import asyncio
import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic_ai import Agent
from pydantic_graph import Graph
from DspyModules.UserRequestAnalyserModule import AnalyzeUserRequestModule
from dto import ChatRequest, ChatResponse
from model import model
from pydantic_ai.mcp import MCPServerHTTP
from prompt import chat_interface_prompt
from chat_history_manager import ChatHistoryManager

from workflow_graph import AssignEntitySchema, ExtractReportReuest, GenerateChart, GenerateGraphQlQuery, PerformAggregation, ResolveError, State, validateGraphQlQuery, ExecuteGraphQlQuery, GenerateExcelReport

from pydantic_ai.messages import (
    ModelMessage,
    ModelRequest,
    ModelResponse,
    TextPart,
    UserPromptPart,
)

import logfire

logfire.configure()
logfire.instrument_pydantic_ai()

server = MCPServerHTTP(url="http://127.0.0.1:8000/sse")

chat_interface_agent = Agent(model, system_prompt= chat_interface_prompt, model_settings= {
    "temperature": 0.3, "timeout": 30, "top_p": 0.9
}, mcp_servers=[server])

@chat_interface_agent.tool_plain(name="process_data_request", require_parameter_descriptions= True, docstring_format="google" )
def process_data_request(user_input: str) -> str:
    """
    Processes a consolidated user request in plain English. The input should include all details provided by the user, such as requested data, filters, and whether the user wants to generate a report, a chart, or simply retrieve data. The function analyzes the request and determines the appropriate workflow.

    Args:
        user_input: A plain English statement fully describing the user's request, including any instructions to generate a report, chart, or just fetch data.
    """
    analyzer_module = AnalyzeUserRequestModule()
    result = analyzer_module(input=user_input)

    state = State(
        input=user_input,
        should_report_be_created=result.should_generate_report,
        should_chart_be_created=result.should_generate_chart,
        aggregate_operation=result.aggregate_operation,
    )
    # Create the graph and run it
    query_generation_graph = Graph(nodes=(AssignEntitySchema, ExtractReportReuest, GenerateGraphQlQuery, validateGraphQlQuery, ResolveError, ExecuteGraphQlQuery, GenerateExcelReport, GenerateChart, PerformAggregation))
    result = query_generation_graph.run_sync(AssignEntitySchema(), state=state)
    return result.output

chat_history_manager = ChatHistoryManager()  # Use ChatHistoryManager for API mode 

# Only used for CLI mode
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

app = FastAPI(
    title="AI Chat Interface API",
    description="API for interacting with the AI reporting system",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:4200"],  # Your Angular app URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/chat", 
    response_model=ChatResponse,
    summary="Chat with AI Assistant",
    description="Send a message to the AI assistant and get a response. The assistant can generate GraphQL queries and reports based on your request."
)
async def chat_endpoint(request: ChatRequest):
    session_id = request.session_id 
    # Retrieve history for this session
    history = chat_history_manager.get_history(session_id)
    async with chat_interface_agent.run_mcp_servers():
        result = await chat_interface_agent.run(request.message, message_history=history)
    # Add user and AI messages to the session history
    from pydantic_ai.messages import ModelRequest, ModelResponse, TextPart, UserPromptPart
    chat_history_manager.add_message(session_id, ModelRequest(parts=[UserPromptPart(content=request.message)]))
    chat_history_manager.add_message(session_id, ModelResponse(parts=[TextPart(content=result.data)]))
    return {"response": result.data}

@app.get("/downloadexcelreport/{report_id}")
def download_report(report_id: str):
    file_path = f"C:\\PydanticAiReporting\\FileStorage\\{report_id}.xlsx"
    if os.path.exists(file_path):
        return FileResponse(path=file_path, filename=f"{report_id}.xlsx", media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    else:
        raise HTTPException(status_code=404, detail="Report not found")

@app.get("/downloadchartpdf/{chart_id}")
def download_report(chart_id: str):
    file_path = f"C:\\PydanticAiReporting\\FileStorage\\{chart_id}.pdf"
    if os.path.exists(file_path):
        return FileResponse(path=file_path, filename=f"{chart_id}.pdf", media_type='application/pdf')
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