from query_generator import query_agent

from strict_user_input_generator import user_input_agent
from bill_schema_graphql import bill_schema_graphql

from pydantic_ai.messages import (
    ModelMessage,
    ModelRequest,
    ModelResponse,
    TextPart,
    UserPromptPart,
)

chat_history : list[ModelMessage] = []  # Use a list to store messages 

# Chat loop
while True:
    query = input("You: ")
    if query.lower() == "exit":
        break
    chat_history.append(ModelRequest(parts=[UserPromptPart(content=query)]))  # Add user message

    # Get AI response using history
    user_request = user_input_agent.run_sync(query, message_history = chat_history).data
    complete_request = "\n### user request:\n" + user_request + " " + "\n### GraphQL Schema:\n" + bill_schema_graphql

    result = query_agent.run_sync(complete_request)  
    chat_history.append(ModelResponse(parts=[TextPart(content=result.data)]))  # Add AI message

    print(f"AI: {result.data}")
