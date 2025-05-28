import dspy
from dspy.teleprompt import BootstrapFewShot
from dspy.evaluate.metrics import answer_exact_match

from DspyModules.QueryGeneratorModule import QueryGenerator
from Schema.full_chema_graphql import full_schema
from dto import ReportRequest, AndCondition, OrCondition, RelatedEntity, SortCondition
from Examples.query_generator_examples import example_list
    
def custom_exact_match(example, prediction, trace=None):
    print("prediction",prediction, example)
    return prediction.query.strip() == example.query.strip()

query_model = QueryGenerator()

tuner = BootstrapFewShot(metric=custom_exact_match, max_labeled_demos= 5, max_rounds=3)

dataset = [dspy.Example(graphql_schema = full_schema, request=ex.input['request'], query=ex.output).with_inputs("graphql_schema","request") for ex in example_list]

trained_query_generator = tuner.compile(query_model, trainset= dataset)

report_request = ReportRequest(
    main_entity='Bill',
    fields_to_fetch_from_main_entity=['amount', 'dueDate', 'number', 'month'],
    or_conditions=[
        OrCondition(entity='Customer', field='name', operation='startsWith', value='v'),
        OrCondition(entity='Account', field='type', operation='eq', value='DOMESTIC')
    ],
    and_conditions=[
        AndCondition(entity='Bill', field='amount', operation='gt', value=500)
    ],
    related_entity_fields=[
        RelatedEntity(entity='Customer', fields=['name'])
    ],
    sort_field_order=None
)

report_request2 =ReportRequest (
    main_entity='Bill',
    fields_to_fetch_from_main_entity=['amount'],
    or_conditions=None,
    and_conditions=None,
    related_entity_fields=None,
    sort_field_order=[
        SortCondition(
            entity='Bill',
            field='amount',
            order='DESC',
        ),
    ],
)


result = trained_query_generator(
    graphql_schema= full_schema ,
    request = report_request2
)

print(result.query)
