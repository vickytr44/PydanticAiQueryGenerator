from __future__ import annotations as _annotations

import asyncio
from dataclasses import dataclass, field
from typing import Any, List

from pydantic_graph import BaseNode, End, Graph, GraphRunContext

from DspyModules.ErrorResolverModule import ErrorResolverModule
from DspyModules.JsonToExcelConverter import SchemaInferenceModule
from DspyModules.QueryGeneratorModule import QueryGenerator
from DspyModules.ReportRequestExtractorModule import ReportRequestExtractor
from dto import ReportRequest
from graphql_client import execute_graphql_query
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
    is_query_validated: bool = field(default=False)


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
        print("Extracting report request...", result.report_request)
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

        print("Validating query...", self.query_to_be_validated)
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

    async def run(self, ctx: GraphRunContext[State]) -> GenerateExcelReport:

        result = execute_graphql_query(self.query_to_execute)
        return GenerateExcelReport(result)
    
@dataclass
class GenerateExcelReport(BaseNode[State, None, str]):
    data_as_json: Any

    async def run(self, ctx: GraphRunContext[State]) -> End[str]:
        print("Generating Excel report...")

        schema_module = SchemaInferenceModule()
        # Call the module
        result = schema_module.forward(raw_json=self.data_as_json)

        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")

        # Save Excel
        with open(f"C:\\PydanticAiReporting\\FileStorage\\report_{timestamp}.xlsx", "wb") as f:
            f.write(result["binary_output"])
        
        return End("File has been generated successfully")

async def main():
    while True:
        # input="get bill amount, duedate, number and month along with customer name and account type where amount is greater than 1000 and customer name starts with 'v' or account type is domestic"
        query = input("You: ")
        if query.lower() == "exit":
            break
        state = State(query)
        query_generation_graph = Graph(nodes=(AssignEntitySchema, ExtractReportReuest, GenerateGraphQlQuery, validateGraphQlQuery, ResolveError, ExecuteGraphQlQuery, GenerateExcelReport))
        result = await query_generation_graph.run(AssignEntitySchema(), state=state)
        print("Ai:",result.output)

asyncio.run(main())