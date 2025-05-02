from __future__ import annotations as _annotations

import asyncio
from dataclasses import dataclass, field
from typing import List

from pydantic_graph import BaseNode, End, Graph, GraphRunContext

from QueryGeneratorModule import QueryGenerator
from ReportRequestExtractorModule import ReportRequestExtractor
from dto import ReportRequest
from model import model
from full_chema_graphql import full_schema
from query_validator import validate_graphql_query_for_workflow
from signature_definition_using_dspy import error_resolver_model
from graphql.error import GraphQLError

@dataclass
class State:
    input: str = field(default="")
    retry_count: int = field(default=0)
    is_initial_query_validated: bool = field(default=False)

@dataclass
class ExtractReportReuest(BaseNode[State]):

    async def run(self, ctx: GraphRunContext[State]) -> GenerateGraphQlQuery:

        extractor = ReportRequestExtractor()

        result = extractor(
        user_input= ctx.state.input,
        graphQl_schema= full_schema
        )
        print("Extracting the report request", result.report_request)
        ctx.state.is_initial_query_generated = result.report_request
        return GenerateGraphQlQuery(result.report_request)
    
@dataclass
class GenerateGraphQlQuery(BaseNode[State, None, str]):
    user_request: ReportRequest

    async def run(self, ctx: GraphRunContext[State]) -> validateGraphQlQuery:

        query_model = QueryGenerator()
        result = query_model(
            graphql_schema= full_schema ,
            request = self.user_request
        )
        print("Generating query", result.query)
        ctx.state.is_initial_query_generated = True
        return validateGraphQlQuery(user_request=self.user_request,query_to_be_validated= result.query)
    
@dataclass
class validateGraphQlQuery(BaseNode[State, None, str]):
    user_request: ReportRequest
    query_to_be_validated: str

    async def run(self, ctx: GraphRunContext[State]) -> End[str] | ResolveError:

        validation_error = validate_graphql_query_for_workflow(self.query_to_be_validated, full_schema)
        print("validation error", validation_error)
        
        ctx.state.is_initial_query_validated = True
        if validation_error is None:
            return End(self.query_to_be_validated)
        else:
            ctx.state.retry_count += 1
            if ctx.state.retry_count > 3:
                return End("Unable to generate a valid GraphQL query for the user request.")
            return ResolveError(user_request=self.user_request, validation_error=validation_error, query_to_be_Resolved=self.query_to_be_validated)
        
@dataclass
class ResolveError(BaseNode[State, None, str]):
    user_request: ReportRequest
    query_to_be_Resolved: str
    validation_error: List[GraphQLError]

    async def run(self, ctx: GraphRunContext[State]) -> validateGraphQlQuery:

        result= error_resolver_model(graphql_schema=full_schema, request = self.user_request, validation_error = self.validation_error, initial_query= self.query_to_be_Resolved)
        print("Generating query", result.query)
        ctx.state.is_initial_query_validated = False
        return validateGraphQlQuery(user_request= self.user_request, query_to_be_validated= result.query)


async def main():
    state = State(input="get bill amount, duedate, number and month along with customer name and account type where amount is greater than 1000 and customer name starts with 'v' or account type is domestic")
    query_generation_graph = Graph(nodes=(ExtractReportReuest, GenerateGraphQlQuery, validateGraphQlQuery, ResolveError))
    result = await query_generation_graph.run(ExtractReportReuest(), state=state)
    print(result.output)

asyncio.run(main())