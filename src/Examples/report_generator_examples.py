import dspy

from src.Schema.full_chema_graphql import full_schema
from src.dto import AndCondition, RelatedEntity, ReportRequest

extract_report_example1 = dspy.Example(
    input={
        'user_input': "get account type and number along with customer name where amount is greater than 1000",
        'graphQl_schema': full_schema
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
        'graphQl_schema': full_schema        
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
        'graphQl_schema': full_schema        
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

extract_report_example4 = dspy.Example(
    input={
        'user_input': "get me customer with bill amount less than 1000",
        'graphQl_schema':  full_schema       
    },
    output=ReportRequest(
        main_entity='Customer',
        fields_to_fetch_from_main_entity=["id", "name", "identityNumber", "age"],
        or_conditions= None,
        and_conditions= [AndCondition(entity='Bill', field='amount', operation='some', value={"lt": 1000})],
        related_entity_fields=[
            RelatedEntity(entity='Bills', fields=['amount'])
        ],
        sort_field_order=None
    )
)

extract_report_example5 = dspy.Example(
    input={
        'user_input': "What is the total bill amount?",
        'graphQl_schema':  full_schema       
    },
    output=ReportRequest(
        main_entity='Bill',
        fields_to_fetch_from_main_entity=["amount"],
        or_conditions= None,
        and_conditions= None,
        related_entity_fields=[],
        sort_field_order=None
    )
)

extract_report_example6 = dspy.Example(
    input={
        'user_input': "What is the total bill amount for commercial account?",
        'graphQl_schema':  full_schema       
    },
    output=ReportRequest(
        main_entity='Bill',
        fields_to_fetch_from_main_entity=["amount"],
        or_conditions= None,
        and_conditions= [
            AndCondition(entity="Account", field="type", operation="eq", value="COMMERCIAL")
        ],
        related_entity_fields=[],
        sort_field_order=None,
        include_count=False
    )
)



extract_report_examples = [extract_report_example1, extract_report_example2, extract_report_example3, extract_report_example4, extract_report_example5]