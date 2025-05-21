import os
from dotenv import load_dotenv
import dspy
import pandas as pd


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

class ChartClarificationSignature(dspy.Signature):
    user_input = dspy.InputField(desc="The user's request for a chart")
    data_sample = dspy.InputField(desc="A preview of the data")
    
    chart_type = dspy.OutputField(desc="Chart type: bar, pie, line")
    x_col = dspy.OutputField(desc="X-axis column value in the data")
    y_col = dspy.OutputField(desc="Y-axis column (for bar/line), or value column (for pie) in the data")
    needs_clarification: bool = dspy.OutputField(desc="True if input is vague, else false")
    clarification_question = dspy.OutputField(desc="Ask this if input is unclear")

class ChartClarifier(dspy.Module):
    def __init__(self):
        super().__init__()
        self.selector = dspy.Predict(ChartClarificationSignature)

    def forward(self, input, df):
        data_sample = df.head(5).to_dict(orient="records")
        return self.selector(user_input=input, data_sample=data_sample)
    

df = pd.read_excel("C:\\PydanticAiReporting\\FileStorage\\report.xlsx")

chart_clarifier = ChartClarifier()
input = "Generate a bar chart for bill amount for all the customers"

result = chart_clarifier(input, df)
print(result)


