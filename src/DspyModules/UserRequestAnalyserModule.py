import os
from typing import Literal
from dotenv import load_dotenv
import dspy


load_dotenv(override=True)

model_name = os.getenv("MODEL_NAME")
azure_endpoint= os.getenv("AZURE_OPENAI_ENDPOINT")
api_key=os.getenv("AZURE_OPENAI_API_KEY")
version = os.getenv("OPENAI_API_VERSION")

lm = dspy.LM(
    model=f"azure/{model_name}",
    api_key=api_key,
    api_base=azure_endpoint,
    api_version=version,
    temperature=0.3,
    top_p=0.95,
    cache= False,
    cache_in_memory=False,
)

dspy.settings.configure(lm=lm, trace=["Test"])

class AnalyzeUserRequestSignature(dspy.Signature):
    """    
    Analyzes user input to determine if report/chart generation is requested.
    
    Args:
        user_input: The user's input text containing information about report/chart generation or just requesting data.
        
    Returns:
        - should_generate_report (bool): True if report generation is explicitly requested
        - should_generate_chart (bool): True if chart generation is explicitly requested
        - requesting_data (bool): True if the user is just requesting data
        - aggregate_operation (str): The type of aggregation operation requested
    """
    user_input: str = dspy.InputField(desc="The user input text containing information about report/chart generation or just requesting data.")
    should_generate_report: bool = dspy.OutputField(desc="True if report generation is explicitly requested", type=bool)
    should_generate_chart : bool = dspy.OutputField(desc="True if chart generation is explicitly requested", type=bool)
    requesting_data : bool = dspy.OutputField(desc="True if the user is just requesting data", type=bool)
    aggregate_operation: Literal["sum", "mean", "std", "variance", "median", "nunique"] | None = dspy.OutputField(desc="The type of aggregation operation requested", default=None)

class AnalyzeUserRequestModule(dspy.Module):
    def __init__(self):
        super().__init__()
        # Initialize the ChainOfThought model with the signature
        self.analyzer = dspy.ChainOfThought(AnalyzeUserRequestSignature)

    def forward(self, input: str):
        # Call the model with the inputs and return the output
        return self.analyzer(user_input=input)


# chart_agent = AnalyzeUserRequestModule()

# input = "Generate a pie chart for this data"
# # input = "Generate a report for bills of customer named virat"
# # input = "give me bills of customer named virat"
# result = chart_agent(input)

# print("Analysis:", result)
