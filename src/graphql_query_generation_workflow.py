from __future__ import annotations as _annotations

from dataclasses import dataclass, field
from typing import List

from pydantic_graph import BaseNode, End, Graph, GraphRunContext

from DspyModules.Helpers.LoadOptimizedPrograms import load_optimized_error_resolver_program, load_optimized_query_generator_program
from DspyModules.ReportRequestExtractorModule import ReportRequestExtractor
from dto import ReportRequest
from Schema.full_chema_graphql import full_schema
from query_validator import validate_graphql_query_for_workflow

import logfire

logfire.configure()
logfire.instrument_pydantic_ai()

# Load the graphql schema that you want to work with
# Replace with your actual schema definition
schema = full_schema

@dataclass
class State:
    input: str = field(default="")
    schema: str = field(default="")
    retry_count: int = field(default=0)
    report_request: ReportRequest = field(default=None)
    is_query_validated: bool = field(default=False)

# Node that helps to extract the request from the user into a structured format
@dataclass
class ExtractReportReuest(BaseNode[State]):

    async def run(self, ctx: GraphRunContext[State]) -> GenerateGraphQlQuery:

        extractor = ReportRequestExtractor()

        result = extractor(
        user_input= ctx.state.input,
        graphQl_schema= schema
        )
        ctx.state.report_request = result.report_request
        return GenerateGraphQlQuery(result.report_request)

# Node that helps to generate the GraphQL query from the structured report request
@dataclass
class GenerateGraphQlQuery(BaseNode[State, None, str]):
    user_request: ReportRequest

    async def run(self, ctx: GraphRunContext[State]) -> validateGraphQlQuery:

        query_model = load_optimized_query_generator_program()
        result = query_model(
            graphql_schema= schema ,
            request = self.user_request
        )
        return validateGraphQlQuery(user_request=self.user_request,query_to_be_validated= result.query)
    
# Node that validates the generated GraphQL query
@dataclass
class validateGraphQlQuery(BaseNode[State, None, str]):
    user_request: ReportRequest
    query_to_be_validated: str

    async def run(self, ctx: GraphRunContext[State]) -> ResolveError | End[str]:

        result = validate_graphql_query_for_workflow(query=self.query_to_be_validated, schema_str=schema)

        ctx.state.is_query_validated = True
        if result is None:
            return End(self.query_to_be_validated)
        else:
            ctx.state.retry_count += 1
            if ctx.state.retry_count > 3:
                return End("Unable to generate a valid GraphQL query for the user request.")
            return ResolveError(user_request=self.user_request, validation_error=result, query_to_be_Resolved=self.query_to_be_validated)

# Node that helps to resolve errors in the GraphQL query
@dataclass
class ResolveError(BaseNode[State, None, str]):
    user_request: ReportRequest
    query_to_be_Resolved: str
    validation_error: List[str]

    async def run(self, ctx: GraphRunContext[State]) -> validateGraphQlQuery:

        optimized_error_resolver = load_optimized_error_resolver_program()
        corrected_query = optimized_error_resolver(
            graphql_schema=schema,
            request=self.user_request,
            validation_error= self.validation_error,
            initial_query= self.query_to_be_Resolved
        )

        ctx.state.is_query_validated = False
        return validateGraphQlQuery(user_request= self.user_request, query_to_be_validated= corrected_query.query)  
    
query_generation_graph = Graph(nodes=(ExtractReportReuest, GenerateGraphQlQuery, validateGraphQlQuery, ResolveError))

# # Option 1: Display as image in Jupyter notebook
# display(Image(query_generation_graph.mermaid_code(start_node=ExtractReportReuest)))

# # Option 2: Print the raw Mermaid code
# print("Mermaid Code:")
# mermaid_code = query_generation_graph.mermaid_code(start_node=ExtractReportReuest)
# print(mermaid_code)

user_prompt = "Generate a chart to visualize how bill amount varies from month to month for the commercial account of John."

result = query_generation_graph.run_sync(ExtractReportReuest(), state=State(input=user_prompt, schema=schema))

print("Final GraphQL Query:", result.output)