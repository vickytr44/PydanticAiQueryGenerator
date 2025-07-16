import dspy

from src.Schema.full_chema_graphql import full_schema
from src.dto import AndCondition, OrCondition, RelatedEntity, ReportRequest

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
        or_conditions=None,
        and_conditions=[
            AndCondition(entity="Account", field="type", operation="eq", value="COMMERCIAL")
        ],
        related_entity_fields=[],
        sort_field_order=None,
        include_count=False
    ),
    reasoning="The query asks for the 'amount' field from the 'Bill' entity. It includes a filter on the related 'Account' entity, where 'type' equals 'COMMERCIAL'. This filter ensures only bills associated with commercial accounts are included."
)

extract_report_example7 = dspy.Example(
    input={
        'user_input': "Create a chart bill amount and due date where the account type is commercial and customer age is greater than 40.",
        'graphQl_schema': full_schema
    },
    output=ReportRequest(
        main_entity='Bill',
        fields_to_fetch_from_main_entity=['amount', 'dueDate'],
        or_conditions=None,
        and_conditions=[
            AndCondition(entity='Account', field='type', operation='eq', value='COMMERCIAL'),
            AndCondition(entity='Customer', field='age', operation='gt', value=40)
        ],
        related_entity_fields=[],
        sort_field_order=None,
        include_count=False
    ),
    reasoning="The query asks for 'amount' and 'dueDate' fields from the 'Bill' entity. It applies two filters: one on the related 'Account' entity where 'type' equals 'COMMERCIAL', and another on the related 'Customer' entity where 'age' is greater than 40. Both conditions must be true for a bill to be included."
)

extract_report_example8 = dspy.Example(
    input={
        'user_input': "Get bills where either the account type is commercial or the customer name is don.",
        'graphQl_schema': full_schema
    },
    output=ReportRequest(
        main_entity='Bill',
        fields_to_fetch_from_main_entity=['id', 'amount', 'month'],
        or_conditions=[
            OrCondition(entity='Account', field='type', operation='eq', value='COMMERCIAL'),
            OrCondition(entity='Customer', field='name', operation='eq', value='don')
        ],
        and_conditions=None,
        related_entity_fields=[],
        sort_field_order=None,
        include_count=False
    ),
        reasoning="The query asks for 'id', 'amount', and 'month' fields from the 'Bill' entity. It uses two alternative filters: one on the related 'Account' entity where 'type' equals 'COMMERCIAL', and one on the related 'Customer' entity where 'name' equals 'don'. A bill is included if either condition is satisfied."
)

extract_report_example9 = dspy.Example(
    input={
        'user_input': "Get id and number of accounts that are of type domestic and are owned by customer virat.",
        'graphQl_schema': full_schema
    },
    output=ReportRequest(
        main_entity='Account',
        fields_to_fetch_from_main_entity=['id', 'number'],
        or_conditions=None,
        and_conditions=[
            AndCondition(entity='Account', field='type', operation='eq', value='DOMESTIC'),
            AndCondition(entity='Customer', field='name', operation='eq', value='virat')
        ],
        related_entity_fields=[],
        sort_field_order=None,
        include_count=False
    ),
    reasoning = "The query asks for the id and number fields from the Account entity. It also applies two filters: one on the Account entity (type equals 'DOMESTIC') and one on the related Customer entity (name equals 'Virat'). Both filters must be applied together to retrieve the correct accounts."
)


extract_report_examples = [extract_report_example1, extract_report_example2, extract_report_example3, extract_report_example4, extract_report_example5, extract_report_example7, extract_report_example8, extract_report_example9]