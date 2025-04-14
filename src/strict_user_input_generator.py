from dataclasses import dataclass
from pydantic_ai import Agent
from model import model
from pydantic import BaseModel, Field
from typing import Optional, List, Dict

from prompt import strict_user_input_prompt

from pydantic_ai import Agent

@dataclass
class strict_user_input_result:
    strict_user_input: str

@dataclass
class Complete_request_result:
    complete_request: str

class ReportRequest(BaseModel):
    main_entity: str = Field(description="Main entity to fetch data from")
    fields_to_fetch_from_main_entity: str = Field(description="Fields to fetch from the main entity")
    or_conditions: Optional[List[str]] = Field(description= "List of OR conditions")
    and_conditions: Optional[List[str]] = Field(description="List of AND conditions")
    related_entity_fields: Optional[Dict[str, str]] = Field(description="Related entities and their fields to fetch")
    sort_field_order: Optional[Dict[str, str]] = Field(description="Sort field and order")

user_input_agent = Agent(model, result_type= strict_user_input_result, system_prompt= strict_user_input_prompt, model_settings={ "temperature": 0.5, "timeout": 30})

@user_input_agent.tool_plain
def generate_strict_user_input(report_request: ReportRequest) -> str:
    """
    Generate a strict, formatted user query based on structured report input including main entity, filters, and related fields.
    """
    or_condition_line = ""
    and_condition_line = ""
    sort_line = ""

    first_line = f"""
    Fetch all {report_request.main_entity} where:"""

    if(report_request.or_conditions):
        or_condition_line = f"""
        - Any of the following must be true:"""

        for condition in report_request.or_conditions:
            or_condition_line += f"""
        - {condition}""" 
        
    if(report_request.and_conditions):
        and_condition_line = f"""
        - And all of the following must be true:"""
        for condition in report_request.and_conditions:
            and_condition_line += f"""
        - {condition}"""

    include_fields_line = f"""
    Include the following fields:
    - **{report_request.main_entity}**: {report_request.fields_to_fetch_from_main_entity}"""

    if(report_request.related_entity_fields):
        for related_entity, fields in report_request.related_entity_fields.items():
            include_fields_line += f"""
        - **{related_entity}**: {fields}"""

    if(report_request.sort_field_order):
        sort_line = f"""
        Sort results by:"""

        for field, order in report_request.sort_field_order.items():
            sort_line += f"""
        - **{field}** in **{order}** order"""
        
    user_input_strict = first_line + "\n" + or_condition_line + "\n" + and_condition_line + "\n" + include_fields_line + "\n" + sort_line

    return user_input_strict
