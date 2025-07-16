from __future__ import annotations as _annotations

from dataclasses import dataclass, field
import io
from typing import Any, List, Literal

import pandas as pd
from pydantic_graph import BaseNode, End, Graph, GraphRunContext

from DspyModules.ChartClarificationModule import ChartClarifier
from DspyModules.DataAnalysisClarificationModule import DataAnalysisClarifier, perform_analysis
from DspyModules.Helpers.LoadOptimizedPrograms import load_optimized_error_resolver_program, load_optimized_query_generator_program, load_optimized_report_request_extractor_program
from DspyModules.ReportRequestExtractorModule import ReportRequestExtractor
from chart_generator import generate_chart_image
from DspyModules.JsonToExcelConverter import SchemaInferenceModule
from dto import ReportRequest
from graphql_client import IsResponseEmpty, execute_graphql_query
from Schema.full_chema_graphql import full_schema
from query_validator import validate_graphql_query_for_workflow
from datetime import datetime

import logfire
from IPython.display import Image, display

logfire.configure()
logfire.instrument_pydantic_ai()


schema = full_schema

@dataclass
class State:
    input: str = field(default="")
    schema: str = field(default="")
    retry_count: int = field(default=0)
    report_request: ReportRequest = field(default=None)
    is_query_validated: bool = field(default=False)
    should_report_be_created: bool = field(default=False)
    should_chart_be_created: bool = field(default=False)
    aggregate_operation: Literal["sum", "mean", "std", "variance", "median", "nunique"] = field(default=None)

@dataclass
class ExtractReportReuest(BaseNode[State]):

    async def run(self, ctx: GraphRunContext[State]) -> GenerateGraphQlQuery:

        # extractor = load_optimized_report_request_extractor_program()
        extractor = ReportRequestExtractor()

        result = extractor(
        user_input= ctx.state.input,
        graphQl_schema= schema
        )
        ctx.state.report_request = result.report_request
        #print("Extracting report request...", result.report_request)
        return GenerateGraphQlQuery(result.report_request)
    
@dataclass
class GenerateGraphQlQuery(BaseNode[State, None, str]):
    user_request: ReportRequest

    async def run(self, ctx: GraphRunContext[State]) -> validateGraphQlQuery:

        # query_model = QueryGenerator()
        query_model = load_optimized_query_generator_program()
        result = query_model(
            graphql_schema= schema ,
            request = self.user_request
        )
        return validateGraphQlQuery(user_request=self.user_request,query_to_be_validated= result.query)
    
@dataclass
class validateGraphQlQuery(BaseNode[State, None, str]):
    user_request: ReportRequest
    query_to_be_validated: str

    async def run(self, ctx: GraphRunContext[State]) -> ExecuteGraphQlQuery | ResolveError:

        result = validate_graphql_query_for_workflow(query=self.query_to_be_validated, schema_str=schema)

        ctx.state.is_query_validated = True
        if result is None:
            return ExecuteGraphQlQuery(self.query_to_be_validated)
        else:
            ctx.state.retry_count += 1
            if ctx.state.retry_count > 3:
                return End("Unable to generate a valid GraphQL query for the user request.")
            return ResolveError(user_request=self.user_request, validation_error=result, query_to_be_Resolved=self.query_to_be_validated)
        
@dataclass
class ResolveError(BaseNode[State, None, str]):
    user_request: ReportRequest
    query_to_be_Resolved: str
    validation_error: List[str]

    async def run(self, ctx: GraphRunContext[State]) -> validateGraphQlQuery:
        # error_resolver = ErrorResolverModule()

        optimized_error_resolver = load_optimized_error_resolver_program()
        corrected_query = optimized_error_resolver(
            graphql_schema=schema,
            request=self.user_request,
            validation_error= self.validation_error,
            initial_query= self.query_to_be_Resolved
        )

        # print("Generating query", corrected_query.query)
        ctx.state.is_query_validated = False
        return validateGraphQlQuery(user_request= self.user_request, query_to_be_validated= corrected_query.query)


@dataclass
class ExecuteGraphQlQuery(BaseNode[State, None, str]):
    query_to_execute: str

    async def run(self, ctx: GraphRunContext[State]) -> End[str]:

        result = execute_graphql_query(self.query_to_execute)
        if 'errors' in result:
            return End(f"GraphQL query execution error: {result['errors']}")
        is_response_empty = IsResponseEmpty(result)
        if is_response_empty:
            return End("No data found for the given query.")

        return End(result)      
    

query_generation_graph = Graph(nodes=(ExtractReportReuest, GenerateGraphQlQuery, validateGraphQlQuery, ResolveError, ExecuteGraphQlQuery))

# Option 1: Display as image in Jupyter notebook
display(Image(query_generation_graph.mermaid_code(start_node=ExtractReportReuest)))

# Option 2: Print the raw Mermaid code
print("Mermaid Code:")
mermaid_code = query_generation_graph.mermaid_code(start_node=ExtractReportReuest)
print(mermaid_code)

# Option 3: Save to file
with open("workflow_diagram.mmd", "w") as f:
    f.write(mermaid_code)