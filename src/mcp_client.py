import asyncio
from pydantic_ai import Agent
from pydantic_ai.mcp import MCPServerHTTP
from model import model
import logfire

logfire.configure()
logfire.instrument_pydantic_ai()

server = MCPServerHTTP(url="http://127.0.0.1:8000/sse")
metadata_provider_agent = Agent(model, mcp_servers=[server], system_prompt="Use the tools to achieve your task.")

async def main():
    print("Hi. How can I help you?")
    while True:
        user_input = input("You: ")
        if user_input.lower() == "exit":
            break

        async with metadata_provider_agent.run_mcp_servers():  
            result = await metadata_provider_agent.run(user_input)
        print(f"AI: {result.data}")

if __name__ == "__main__":
    asyncio.run(main())