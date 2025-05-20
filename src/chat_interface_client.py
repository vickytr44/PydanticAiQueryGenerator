import asyncio
import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic_ai import Agent
from pydantic_graph import Graph
from dto import ChatRequest, ChatResponse
from model import model
from pydantic_ai.mcp import MCPServerHTTP
from prompt import chat_interface_prompt

from workflow_graph import AssignEntitySchema, ExtractReportReuest, GenerateChart, GenerateGraphQlQuery, ResolveError, State, validateGraphQlQuery, ExecuteGraphQlQuery, GenerateExcelReport

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

@chat_interface_agent.tool_plain(name="process_data_request ", require_parameter_descriptions= True, docstring_format="google" )
def process_data_request (user_input: str, should_generate_report: bool, should_generate_chart: bool, prompt_for_chart_generation: str) -> str:
    """
    Accept a user message in plain English describing the user input. Mention if the user wants to generate a report or not.
    Only set `should_generate_report` to true if the user *explicitly asks* for a report or to "generate a report".
    Only set `should_generate_chart` to true if the user *explicitly asks* for a chart or to "generate a chart".
    populate `prompt_for_chart_generation` with the prompt to be used for chart generation. This is used only when `should_generate_chart` is true.

    Args:
        user_input: Plain English description the user input.
        should_generate_report: Should be true only when the user explicitly asks to generate a report".
        should_generate_chart: Should be true only when the user explicitly asks to generate a chart.
        prompt_for_chart_generation: The prompt to be used for chart generation. This is used only when `should_generate_chart` is true.
    """
    print("Generating GraphQL query...", user_input, "should generate report:", should_generate_report)
    state = State(input=user_input, should_report_be_created=should_generate_report, should_chart_be_created=should_generate_chart, propmt_for_chart=prompt_for_chart_generation)
    # Create the graph and run it
    query_generation_graph = Graph(nodes=(AssignEntitySchema, ExtractReportReuest, GenerateGraphQlQuery, validateGraphQlQuery, ResolveError, ExecuteGraphQlQuery, GenerateExcelReport, GenerateChart))
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
    async with chat_interface_agent.run_mcp_servers():
        result = await chat_interface_agent.run(request.message, message_history=chat_history)
    chat_history.append(ModelRequest(parts=[UserPromptPart(content=request.message)]))
    chat_history.append(ModelResponse(parts=[TextPart(content=result.data)]))
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