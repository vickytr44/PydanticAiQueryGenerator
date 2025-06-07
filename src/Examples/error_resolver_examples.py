import dspy
from src.Schema.full_chema_graphql import full_schema
from src.dto import AndCondition, OrCondition, RelatedEntity, ReportRequest, SortCondition


example1_report_request = ReportRequest(
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
    )

example1_initial_query = """
    {
    bills(
        where: {
        and: [{ amount: { gt: 1000 } }]
        or: [
            { account: { type: { eq: DOMESTIC } } }
            { customer: { name: { startsWith: "v" } } }
        ]
        }}
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

example1_output = """
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

few_shot_example1 = dspy.Example(
    input= {
        'graphql_schema' : full_schema,
        'request' : example1_report_request,
        'validation_error' : ["Syntax Error: Expected Name, found '}'."],
        'initial_query' : example1_initial_query
    },
    output = example1_output 
)

example_request2 = ReportRequest(
        main_entity="bills",
        fields_to_fetch_from_main_entity=["amount", "month"],
        and_conditions= None,
        or_conditions= None,
        related_entity_fields= None,
        sort_field_order=[
            SortCondition(entity="bills", field="duedate", order="desc")
        ]
)

example2_initial_query = """
        {
        bills(order: [{ dueDate: DESC }])] {
            nodes {
            amount
            month
            }
        }
        }
"""

example2_output = """
{
  bills(order: [{ dueDate: DESC }]) {
    nodes {
      amount
      month
    }
  }
}

"""

few_shot_example2 = dspy.Example(
    input= {
        'graphql_schema' : full_schema,
        'request' : example_request2,
        'validation_error' : ["Syntax Error: Expected Name, found ']'."],
        'initial_query' : example2_initial_query
    },
    output = example2_output 
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

sort_initial_query = """
        query {
            customers([order: { age: ASC }], where: { name: { startsWith: "v" } }) {
                nodes {
                age
                id
                identityNumber
                name
                }
            }
        }
    """  

sort_output = """
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

sort_example = dspy.Example(
    input= {
        'graphql_schema' : full_schema,
        'request' : sort_example_request,
        'validation_error' : ["Syntax Error: Expected Name, found '['."],
        'initial_query' : sort_initial_query
    },
    output = sort_output 
)


example_list = [
    few_shot_example1,
    few_shot_example2,
    sort_example
]