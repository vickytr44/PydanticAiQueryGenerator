from __future__ import annotations as _annotations

from dataclasses import dataclass, field
import io
from typing import Any, List, Literal

import pandas as pd
from pydantic_graph import BaseNode, End, Graph, GraphRunContext

from DspyModules.ChartClarificationModule import ChartClarifier
from DspyModules.DataAnalysisClarificationModule import DataAnalysisClarifier, perform_analysis
from chart_generator import generate_chart_image
from DspyModules.ErrorResolverModule import ErrorResolverModule
from DspyModules.JsonToExcelConverter import SchemaInferenceModule
from DspyModules.QueryGeneratorModule import QueryGenerator
from DspyModules.ReportRequestExtractorModule import ReportRequestExtractor
from dto import ReportRequest
from graphql_client import IsResponseEmpty, execute_graphql_query
from model import model
from Schema.full_chema_graphql import full_schema
from Schema.bill_schema_graphql import bill_schema_graphql
from query_validator import validate_graphql_query_for_workflow
from DspyModules.signature_definition_using_dspy import error_resolver_model, validation_model
from graphql.error import GraphQLError
from datetime import datetime


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
class AssignEntitySchema(BaseNode[State]):

    async def run(self, ctx: GraphRunContext[State]) -> ExtractReportReuest:

        ctx.state.schema = schema
        return ExtractReportReuest()

@dataclass
class ExtractReportReuest(BaseNode[State]):

    async def run(self, ctx: GraphRunContext[State]) -> GenerateGraphQlQuery:

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

        query_model = QueryGenerator()
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

        print("Validating query...", self.query_to_be_validated, "retry count:", ctx.state.retry_count)
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
        error_resolver = ErrorResolverModule()

        corrected_query = error_resolver(
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

    async def run(self, ctx: GraphRunContext[State]) -> GenerateExcelReport | GenerateChart | End[str]:

        result = execute_graphql_query(self.query_to_execute)
        is_response_empty = IsResponseEmpty(result)
        if is_response_empty:
            return End("No data found for the given query.")
        print("should report be created?", ctx.state.should_report_be_created)
        if not ctx.state.should_report_be_created and not ctx.state.should_chart_be_created:
            if ctx.state.aggregate_operation is not None:
                return PerformAggregation(data_as_json=result)
            return End(result)
        
        if ctx.state.should_chart_be_created:
            return GenerateChart(data_as_json=result)
        
        return GenerateExcelReport(result)
    

@dataclass
class GenerateChart(BaseNode[State, None, str]):
    data_as_json: Any

    async def run(self, ctx: GraphRunContext[State]) -> End[str]:
        print("Generating chart...", self.data_as_json)

        schema_module = SchemaInferenceModule()
        # Call the module
        result = schema_module.forward(raw_json=self.data_as_json)

        excel_buffer = io.BytesIO(result["binary_output"])
        df = pd.read_excel(excel_buffer)

        chart_clarifier = ChartClarifier()

        chart_clarifier_result = chart_clarifier(ctx.state.input, df)

        if chart_clarifier_result.needs_clarification == True:
            return End({"clarification_needed": True, "question": chart_clarifier_result.clarification_question})

        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")

        # Call general-purpose chart function
        filename = generate_chart_image(
            data=df,
            x_col=chart_clarifier_result.x_col,
            y_col=chart_clarifier_result.y_col,
            chart_type=chart_clarifier_result.chart_type,
            filename=f"chart_{timestamp}"
        )
        
        return End(f"File has been generated successfully. Your chart is ready! Download it here: http://localhost:8080/downloadchartpdf/{filename}")
    
@dataclass
class GenerateExcelReport(BaseNode[State, None, str]):
    data_as_json: Any

    async def run(self, ctx: GraphRunContext[State]) -> End[str]:
        print("Generating Excel report...", self.data_as_json)

        schema_module = SchemaInferenceModule()
        # Call the module
        result = schema_module.forward(raw_json=self.data_as_json)

        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")

        # Save Excel
        with open(f"C:\\PydanticAiReporting\\FileStorage\\report_{timestamp}.xlsx", "wb") as f:
            f.write(result["binary_output"])
        
        return End(f"File has been generated successfully. Your Excel report is ready! Download it here: http://localhost:8080/downloadexcelreport/report_{timestamp}")

@dataclass
class PerformAggregation(BaseNode[State, None, str]):
    data_as_json: Any

    async def run(self, ctx: GraphRunContext[State]) -> End[str]:
        print("Performing aggregation...", ctx.state.aggregate_operation)

        schema_module = SchemaInferenceModule()
        # Call the module
        result = schema_module.forward(raw_json=self.data_as_json)

        excel_buffer = io.BytesIO(result["binary_output"])
        df = pd.read_excel(excel_buffer)

        clarifier = DataAnalysisClarifier()
        result = clarifier(input, df)

        print(result)

        if result.needs_clarification == True:
            return({"clarification_needed": True, "question": result.clarification_question})

        output_df = perform_analysis(df, result.operation, result.group_by_col, result.target_col)
        return End(output_df) 
    

# async def main():
#     while True:
#         # input="get bill amount, duedate, number and month along with customer name and account type where amount is greater than 1000 and customer name starts with 'v' or account type is domestic"
#         query = input("You: ")
#         if query.lower() == "exit":
#             break
#         state = State(query)
#         query_generation_graph = Graph(nodes=( AssignEntitySchema, ExtractReportReuest, GenerateGraphQlQuery, validateGraphQlQuery, ResolveError, ExecuteGraphQlQuery, GenerateExcelReport, PerformAggregation))
#         result = await query_generation_graph.run(AssignEntitySchema(), state=state)
#         print("Ai:",result.output)

# asyncio.run(main())