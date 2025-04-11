from backend_central_dev.task_executor_blueprint import (
    create_service, ExecutorBluePrint)

app = ExecutorBluePrint(
    __name__,
    component_path=__file__
).app
