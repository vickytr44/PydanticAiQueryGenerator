# import os
# from typing import List
# from dotenv import load_dotenv
# import dspy

# load_dotenv(override=True)

# model_name = os.getenv("MODEL_NAME")
# azure_endpoint= os.getenv("AZURE_OPENAI_ENDPOINT")
# api_key=os.getenv("AZURE_OPENAI_API_KEY")
# version = os.getenv("OPENAI_API_VERSION")

# lm = dspy.LM(
#     model=f"azure/{model_name}",
#     api_key=api_key,
#     api_base=azure_endpoint,
#     api_version=version,
#     temperature=0.3,
#     top_p=0.95,
#     cache= False,
#     cache_in_memory=False,
# )

# dspy.settings.configure(lm=lm, trace=["Test"])


# class ShouldReportBeGeneratedSignature(dspy.Signature):
#     """Check if user has implicitly requested to generate a report."""
#     user_request: str = dspy.InputField(desc="User request for data")
#     should_generate_report: bool = dspy.OutputField(desc="True if the user has implicitly requested to generate a report, otherwise False.", type=bool)

# class ShouldReportBeGeneratedModule(dspy.Module):
#     def __init__(self):
#         super().__init__()
#         # Initialize the ChainOfThought model with the signature
#         self.predict = dspy.ChainOfThought(ShouldReportBeGeneratedSignature)

#     def forward(self, user_request):
#         # Call the model with the inputs and return the output
#         return self.predict(
#             user_request= user_request
#         )
