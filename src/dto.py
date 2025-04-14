from pydantic import BaseModel, Field
from typing import List, Dict, Optional

class ReportRequest(BaseModel):
    main_entity: str = Field(description="Main entity to fetch data from")
    fields_to_fetch_from_main_entity: str = Field(description="Fields to fetch from the main entity")
    or_conditions: Optional[List[str]] = Field(default=None, description="List of OR conditions")
    and_conditions: Optional[List[str]] = Field(default=None, description="List of AND conditions")
    related_entity_fields: Optional[Dict[str, str]] = Field(default=None, description="Related entities and their fields to fetch")
    sort_field_order: Optional[Dict[str, str]] = Field(default=None, description="Sort field and order")