from backend_central_dev.task_executor_blueprint import (
    create_service, ExecutorBluePrint)

ebp = ExecutorBluePrint(
    'multi_care_dataset',
    __name__,
    component_path=__file__,
    url_prefix='/multi_care',
)

multi_care = create_service(ebp)
