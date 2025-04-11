from backend_central_dev.task_executor_blueprint import (
    create_service, ExecutorBluePrint)

ebp = ExecutorBluePrint(
    'mimic-cxr-lt_dataset',
    __name__,
    component_path=__file__,
    url_prefix='/mimic-cxr-lt',
)

isic = create_service(ebp)
