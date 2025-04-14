from pydantic_ai import Agent

from model import model
from prompt import query_generation_prompt

query_agent = Agent(model, system_prompt=query_generation_prompt, model_settings={
    "temperature": 0.3, "timeout": 30
})
