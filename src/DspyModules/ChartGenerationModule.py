import os
from typing import Literal
from dotenv import load_dotenv
import dspy
import pandas as pd
import matplotlib.pyplot as plt

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


import io
import matplotlib.pyplot as plt

def generate_chart_image(data, x_col, y_col, chart_type="bar", filename="output_chart.pdf"):
    if x_col not in data.columns or y_col not in data.columns:
        raise ValueError(f"Columns '{x_col}' or '{y_col}' not found in data.")

    plt.figure(figsize=(8, 5))

    if chart_type == "bar":
        grouped = data.groupby(x_col)[y_col].sum()
        grouped.plot(kind="bar", color="skyblue")
    elif chart_type == "line":
        data.plot(x=x_col, y=y_col, kind="line", marker='o')
    elif chart_type == "pie":
        grouped = data.groupby(x_col)[y_col].sum()
        grouped.plot(kind="pie", autopct="%1.1f%%", ylabel='')
    else:
        raise ValueError(f"Unsupported chart type: {chart_type}")

    plt.title(f"{y_col} by {x_col}")

    if chart_type != "pie":
        plt.xlabel(x_col)
        plt.ylabel(y_col)

    plt.tight_layout()
    plt.savefig(f"C:\\PydanticAiReporting\\FileStorage\\{filename}")
    plt.close()

    return filename


class ChartIntentSignature(dspy.Signature):
    """Extract chart generation intent from user input."""
    prompt = dspy.InputField(desc="User's natural language request for a chart.")
    chart_type : Literal["bar", "line", "pie"] = dspy.OutputField(desc="Type of chart to generate, like bar, line, or pie.")
    x_column = dspy.OutputField(desc="Column to use for the X-axis (grouping key).")
    y_column = dspy.OutputField(desc="Column to use for the Y-axis (values to summarize).")

class ChartIntentModule(dspy.Module):
    def __init__(self):
        super().__init__()
        self.extractor = dspy.ChainOfThought(ChartIntentSignature)

    def forward(self, prompt):
        return self.extractor(prompt=prompt)
    

# df = pd.read_excel("C:\\PydanticAiReporting\\FileStorage\\report.xlsx")
# chart_agent = ChartIntentModule()

# prompt = "Generate a pie chart for the data."
# intent = chart_agent(prompt=prompt)

# print("Intent Extracted:", intent)

# # Call general-purpose chart function
# filename = generate_chart_image(
#     data=df,
#     x_col=intent.x_column,
#     y_col=intent.y_column,
#     chart_type=intent.chart_type
# )

# print(f"✅ Chart saved as {filename}")