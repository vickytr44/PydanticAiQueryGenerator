from pydantic_ai import Agent

from model import model
from prompt import query_generation_prompt
from strict_user_input_generator import user_input_agent
from bill_schema_graphql import bill_schema_graphql

user_input = "get bill amount, duedate, number and month along with customer name and account type where amount is greater than 1000 and customer name starts with 'v' or account type is domestic"

user_request = user_input_agent.run_sync(user_input).data

query_agent = Agent(model, system_prompt=query_generation_prompt, model_settings={
    "temperature": 0.3
})

complete_request = "\n### user request:\n" + user_request + " " + "\n### GraphQL Schema:\n" + bill_schema_graphql

result = query_agent.run_sync(complete_request)  

print(result.data)
