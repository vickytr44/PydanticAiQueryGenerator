import dspy
from src.Schema.full_chema_graphql import full_schema
from src.dto import AndCondition, OrCondition, RelatedEntity, ReportRequest, SortCondition


few_shot_example1 = dspy.Example(
    input= {
        'request' : ReportRequest(
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
            SortCondition(entity="bills", field="duedate", order="desc")
        ]
    ),
    'graphql_schema': full_schema
    },
    output= """
    {
    bills(
        where: {
        and: [{ amount: { gt: 1000 } }]
        or: [
            { account: { type: { eq: DOMESTIC } } }
            { customer: { name: { startsWith: "v" } } }
        ]
        }
        order: [{ dueDate: DESC }]
    ) {
        nodes {
        amount
        month
        customer {
            age
        }
        account {
            number
        }
        }
    }
    }
    """ 
)

example_request = ReportRequest(
        main_entity="bills",
        fields_to_fetch_from_main_entity=["amount", "month"],
        and_conditions= None,
        or_conditions= None,
        related_entity_fields= None,
        sort_field_order=[
            SortCondition(entity="bills", field="duedate", order="desc")
        ]
)


few_shot_example2 = dspy.Example(
    input= {
        'request' : example_request,
        'graphql_schema': full_schema
    },
    output= """
        {
        bills(order: [{ dueDate: DESC }]) {
            nodes {
            amount
            month
            }
        }
        }
    """   
)


list_filter_request = ReportRequest(
    main_entity="Customer",
    fields_to_fetch_from_main_entity=["id", "name"],
    and_conditions=[
        AndCondition(entity="bills", field="amount", operation="gt", value=1000)
    ],
    related_entity_fields=[
        RelatedEntity(entity="bills", fields=["amount"])
    ],
    or_conditions= None,
    sort_field_order= None
)

list_filter_example = dspy.Example(
    input= {
        'request' : list_filter_request,
        'graphql_schema': full_schema
    },
    output= """
        query {
        customers(where: { bills: { some: { amount: { gt: 1000 } } } }) {
            nodes {
            id
            name
            bills {
                amount
            }
            }
        }
        }
    """   
)


sort_example_request = ReportRequest(
    main_entity="Customer",
    fields_to_fetch_from_main_entity=[
        "age",
        "id",
        "identityNumber",
        "name"
    ],
    or_conditions=None,
    and_conditions=[
        AndCondition(
            entity="Customer",
            field="name",
            operation="startsWith",
            value="v"
        )
    ],
    related_entity_fields=None,
    sort_field_order=[
        SortCondition(
            entity="Customer",
            field="age",
            order="ASC"
        )
    ]
)

sort_example = dspy.Example(
    input= {
        'request' : sort_example_request,
        'graphql_schema': full_schema
    },
    output= """
        query {
            customers(order: { age: ASC }, where: { name: { startsWith: "v" } }) {
                nodes {
                age
                id
                identityNumber
                name
                }
            }
        }
    """   
)


example_list = [
    few_shot_example1,
    few_shot_example2,
    list_filter_example,
    sort_example
]