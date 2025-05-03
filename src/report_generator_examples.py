import dspy

from account_schema_graphql import account_schema_graphql
from bill_schema_graphql import bill_schema_graphql
from dto import AndCondition, RelatedEntity, ReportRequest

extract_report_example1 = dspy.Example(
    input={
        'user_input': "get account type and number along with customer name where amount is greater than 1000",
        'graphQl_schema': account_schema_graphql
    },
    output=ReportRequest(
        main_entity='Account',
        fields_to_fetch_from_main_entity=['number', 'type'],
        or_conditions=[],
        and_conditions=[AndCondition(entity='Bill', field='amount', operation='gt', value=1000)],
        related_entity_fields=[
            RelatedEntity(entity='Customer', fields=['name'])
        ],
        sort_field_order=None
    )
)

extract_report_example2 = dspy.Example(
    input={
        'user_input': "get bill amount along with customer age and account number",
        'graphQl_schema': bill_schema_graphql        
    },
    output=ReportRequest(
        main_entity='Bill',
        fields_to_fetch_from_main_entity=['amount'],
        or_conditions= None,
        and_conditions= None,
        related_entity_fields=[
            RelatedEntity(entity='Customer', fields=['name']),
            RelatedEntity(entity='Account', fields=['number'])
        ],
        sort_field_order=None
    )
)

extract_report_example3 = dspy.Example(
    input={
        'user_input': "get bill duedate along with customer id and account type",
        'graphQl_schema': bill_schema_graphql        
    },
    output=ReportRequest(
        main_entity='Bill',
        fields_to_fetch_from_main_entity=['dueDate'],
        or_conditions= None,
        and_conditions= None,
        related_entity_fields=[
            RelatedEntity(entity='Customer', fields=['id']),
            RelatedEntity(entity='Account', fields=['type'])
        ],
        sort_field_order=None
    )
)

extract_report_examples = [extract_report_example1, extract_report_example2, extract_report_example3]