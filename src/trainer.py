import dspy
from dspy.teleprompt import BootstrapFewShot

import Schema.account_schema_graphql as account_schema_graphql
from Schema.bill_schema_graphql import bill_schema_graphql
from dto import ReportRequest, AndCondition, OrCondition, RelatedEntity, SortCondition
from DspyModules.signature_definition_using_dspy import extract_report_request
    
few_shot_example = dspy.Example(
    input={
        'user_input': "Get bill amount and month along with customer age and account number where amount is greater than 1000 and (customer name starts with 'v' or account type is domestic) ordered by due date descending",
        'graphQl_schema': bill_schema_graphql
    },
    output=ReportRequest(
        main_entity="bills",
        fields_to_fetch_from_main_entity=["amount", "month"],
        and_conditions=[
            AndCondition(entity="bills", field="amount", operation="gt", value=1000),
        ],
        or_conditions=[
            OrCondition(entity="account", field="type", operation="eq", value="DOMESTIC"),            
            OrCondition(entity="customer", field="name", operation="startsWith", value="v")
        ],
        related_entity_fields=[
            RelatedEntity(entity="customer", fields=["age"]),
            RelatedEntity(entity="account", fields=["number"])
        ],
        sort_field_order=[
            SortCondition(entity="bills", field="due_date", order="desc")
        ]
    )
)

trainset = [
    few_shot_example
]

tuner = BootstrapFewShot

new_extract_report_request = tuner.compile(extract_report_request, trainset=trainset)


# Generate queries based on user input
input="get all accounts number and type along with customer name and age where customer name starts with 'v' and age is greater than 30"
result = new_extract_report_request(user_input=input, graphQl_schema=account_schema_graphql)
print(result.report_request)