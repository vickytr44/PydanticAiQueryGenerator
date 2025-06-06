from pydantic import BaseModel, Field
from typing import Any, List, Optional
from enum import Enum

class Entity(Enum):
    Account = "accounts",
    Customer = "customers",
    Bill = "bills"

class OrCondition(BaseModel):
    entity: str = Field(description="Entity for the OR condition")
    field: str = Field(description="Field for the OR condition")
    operation: str = Field(description="Operation for the OR condition")
    value: Any = Field(description="Value for the OR condition")

class AndCondition(BaseModel):
    entity: str = Field(description="Entity for the AND condition")
    field: str = Field(description="Field for the AND condition")
    operation: str = Field(description="Operation for the AND condition")
    value: Any = Field(description="Value for the AND condition")

class RelatedEntity(BaseModel):
    entity: str = Field(description="Related entity name")
    fields: List[str] = Field(description="Fields to fetch from the related entity")

class SortCondition(BaseModel):
    entity: str = Field(description="Entity to sort by")
    field: str = Field(description="Field to sort by")
    order: str = Field(description="Order of sorting (asc/desc)")

class ReportRequest(BaseModel):
    main_entity: str = Field(description="Main entity to fetch data from")
    fields_to_fetch_from_main_entity: List[str] = Field(description="Fields to fetch from the main entity")
    or_conditions: Optional[List[OrCondition]] = Field(default=None, description="List of OR conditions")
    and_conditions: Optional[List[AndCondition]] = Field(default=None, description="List of AND conditions")
    related_entity_fields: Optional[List[RelatedEntity]] = Field(default=None, description="Related entities and their fields to fetch")
    sort_field_order: Optional[List[SortCondition]] = Field(default=None, description="Sort entity, field and order")
    include_count: bool = Field(default=False,description="Whether to include the count of records fetched")

class ChatRequest(BaseModel):
    message: str = Field(
        description="The message to send to the AI assistant",
        example="Generate a report about sales data"
    )
    session_id: str = Field(
        ...,
        description="The session ID for the chat history. Use a unique value per user or conversation.",
        example="chat_session_00001"
    )

class ChatResponse(BaseModel):
    response: str = Field(
        description="The AI assistant's response",
        example="I have generated a report based on the sales data..."
    )