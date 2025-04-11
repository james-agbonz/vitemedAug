from backend_central_dev.task_executor_blueprint import (
    create_service, ExecutorBluePrint)

ebp = ExecutorBluePrint(
    'isic_dataset',
    __name__,
    component_path=__file__,
    url_prefix='/isic',
)

isic = create_service(ebp)
