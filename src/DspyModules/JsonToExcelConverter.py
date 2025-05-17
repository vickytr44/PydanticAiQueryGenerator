import os
from typing import Any, List
from dotenv import load_dotenv
import dspy
import pandas as pd
import io
import json
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
    cache= False
)

dspy.settings.configure(lm=lm, trace=["Test"])

class SchemaInferenceSignature(dspy.Signature):
    """Infers tabular schema from raw JSON data and returns a structured table."""

    raw_json: Any = dspy.InputField(desc="List of JSON objects to infer schema from.")
    
    tabular_rows : List[List[str]] = dspy.OutputField(desc="Table as list of rows (header + data)", type=List[List[str]])


class SchemaInferenceModule(dspy.Module):
    def __init__(self):
        super().__init__()
        self.infer_schema = dspy.ChainOfThought(SchemaInferenceSignature)    

    def forward(self, raw_json: str) -> dict:
        # Step 1: Ask LLM to infer schema and return table as JSON array of arrays
        response = self.infer_schema(raw_json=raw_json)

        # Step 2: Parse the LLM output, which should be a JSON list of lists
        try:
            # If your OutputField is typed, DSPy might have already parsed tabular_rows into a list.
            # So first check if it's already a list:
            tabular_data = response.tabular_rows

            if isinstance(tabular_data, str):
                # If still a string, parse JSON:
                tabular_data = json.loads(tabular_data)

            # Validate minimal structure: at least header + one row
            if not (isinstance(tabular_data, list) and len(tabular_data) > 1 and all(isinstance(row, list) for row in tabular_data)):
                raise ValueError("Tabular data is not a list of lists or too short")

            # Create DataFrame using first row as columns
            df = pd.DataFrame(tabular_data[1:], columns=tabular_data[0])
        except Exception as e:
            raise ValueError(f"Failed to parse LLM output: {e}\nLLM Output:\n{response.tabular_rows}")

        # Step 3: Convert to Excel binary stream
        output = io.BytesIO()
        df.to_excel(output, index=False)
        output.seek(0)

        return {"binary_output": output.read()}

# schema_module = SchemaInferenceModule()

# # Raw JSON input
# sample_json = """
# [
#   {"fullName": "Alice Smith", "age": 30, "location": "NY"},
#   {"fullName": "Bob Johnson", "age": 25, "location": "CA"}
# ]
# """

# # Call the module
# result = schema_module.forward(raw_json=sample_json)

# # Save Excel
# with open("output.xlsx", "wb") as f:
#     f.write(result["binary_output"])