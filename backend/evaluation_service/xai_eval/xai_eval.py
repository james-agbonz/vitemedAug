from backend_central_dev.constant import TaskStatus


def _xai_eval(task_ticket, publisher_endpoint_url, task_parameters):
    print(task_ticket, publisher_endpoint_url, task_parameters)
    return TaskStatus.finished
