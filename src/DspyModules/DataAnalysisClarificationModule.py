import os
from typing import Literal
from dotenv import load_dotenv
import pandas as pd
import logfire

load_dotenv(override=True)

logfire.configure(
    service_name="my_dspy_service",
    send_to_logfire=True,
)

#logfire.install_auto_tracing(modules=["dspy"], min_duration=1, check_imported_modules="warn")

import dspy

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

def perform_analysis(df, op, group_by_col=None, target_col=None):
    with logfire.span("perform aggregate operation"):  # Add tracing span
        # Normalize invalid group_by_col
        if group_by_col is None or group_by_col == "N/A" or group_by_col.strip() == "":
            if op in ["mean", "sum", "std", "Variance", "median", "nunique"]:
                result = pd.DataFrame({target_col: [df[target_col].agg(op)]}).to_dict(orient="records")
                logfire.info(f"Performing {op} on {target_col} grouped by {group_by_col}, result: {result}")
                return result
            else:
                WarningText = f"Unsupported operation without grouping: {op}"
                logfire.warning(WarningText)
                return WarningText
        
        if op == "mean":
            return df.groupby(group_by_col)[target_col].mean().reset_index().to_dict(orient="records")
        elif op == "sum":
            return df.groupby(group_by_col)[target_col].sum().reset_index().to_dict(orient="records")
        elif op == "std":
            return df.groupby(group_by_col)[target_col].std().reset_index().to_dict(orient="records")
        elif op == "Variance":
            return df.groupby(group_by_col)[target_col].var().reset_index().to_dict(orient="records")
        elif op == "median":
            return df.groupby(group_by_col)[target_col].median().reset_index().to_dict(orient="records")
        elif op == "nunique":
            return df.groupby(group_by_col)[target_col].nunique().reset_index().to_dict(orient="records")
        else:
            return (f"Unsupported operation: {op}")

class DataAnalysisSignature(dspy.Signature):
    user_prompt = dspy.InputField(desc="The user’s data analysis request")
    data_sample = dspy.InputField(desc="Sample of the tabular data")

    operation: Literal["sum", "mean", "std", "variance", "median", "nunique"] = dspy.OutputField(desc="The type of analysis operation to perform.")
    group_by_col : str | None = dspy.OutputField(desc="The column name in the data to group by, if any", default= None)
    target_col = dspy.OutputField(desc="The numeric column name in the data to apply the operation on.")
    needs_clarification : bool = dspy.OutputField(desc="true if the intent is vague, else false", type=bool)
    clarification_question = dspy.OutputField(desc="What question should be asked if clarification is needed?")

class DataAnalysisClarifier(dspy.Module):
    def __init__(self):
        super().__init__()
        self.analyzer = dspy.Predict(DataAnalysisSignature)

    def forward(self, user_prompt, df):
        with logfire.span("DataAnalysisClarifier") as span:  # Add tracing span
            sample = df.head(5).to_dict(orient="records")
            result = self.analyzer(user_prompt=user_prompt, data_sample=sample)
            logfire.info(f"User prompt: {user_prompt}, Sample data: {sample}, Analyzer result: {result}")
            return result
    
# df = pd.read_excel("C:\\PydanticAiReporting\\FileStorage\\report.xlsx")
# print(df)
# input = "get me the averge bill amount for all the customers"
# clarifier = DataAnalysisClarifier()
# result = clarifier(input, df)

# print(result)

# if result.needs_clarification == "YES":
#     print({"clarification_needed": True, "question": result.clarification_question})
# with logfire.span("My DSPy Module"):
#     output_df = perform_analysis(df, result.operation, result.group_by_col, result.target_col)
    
# print(output_df)
