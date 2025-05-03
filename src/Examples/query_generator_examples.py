import dspy
import Schema.bill_schema_graphql as bill_schema_graphql
from dto import AndCondition, OrCondition, RelatedEntity, ReportRequest, SortCondition


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
            SortCondition(entity="bills", field="due_date", order="desc")
        ]
    ),
    'graphql_schema': bill_schema_graphql
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
            SortCondition(entity="bills", field="due_date", order="desc")
        ]
)

few_shot_example2 = dspy.Example(
    input= {
        'request' : example_request,
        'graphql_schema': bill_schema_graphql
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