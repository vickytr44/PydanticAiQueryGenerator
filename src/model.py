import os
from openai import AsyncAzureOpenAI

from pydantic_ai import Agent
from pydantic_ai.models.openai import OpenAIModel
from pydantic_ai.providers.openai import OpenAIProvider

from dotenv import load_dotenv

load_dotenv(override=True)

client = AsyncAzureOpenAI(
    azure_endpoint= os.getenv("AZURE_OPENAI_ENDPOINT"),
    api_version=os.getenv("OPENAI_API_VERSION"),
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
)

model_name = os.getenv("MODEL_NAME")

print("Model Name: ", model_name)

model = OpenAIModel(
    model_name,
    provider=OpenAIProvider(openai_client=client)
)