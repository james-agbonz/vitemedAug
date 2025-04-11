import requests
from backend_central_dev.constant import *
import json


def prety_print_json(json_data):
    return json.dumps(json_data, indent=4)


def print_prety_json(json_data):
    print(prety_print_json(json_data))


def add_action_to_command(parser, choices=['plan', 'apply', 'destroy']):
    parser.add_argument(
        "action", help="action to perform", choices=choices)


def get_entity_list(central_url, entity_name):
    response = requests.get(f"{central_url}/task_publisher/{entity_name}")
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Failed to get service info list: {response.text}")
        return []


def get_id_by_name(name, list, name_key, id_key):
    if name is not None:
        for item in list:
            # print(item[name_key].lower(), name.lower())
            if item[name_key].lower() == name.lower():
                return item[id_key]
    return None


def service_reg_request(central_url, services):
    print("Registering services to central, central url:", central_url)

    def make_service_reg_request(central_url, service_url, service_name, service_type):
        response = requests.post(f"{service_url}/{service_name}/register_to_central", json={
            'central_url': central_url,
            'service_url': service_url,
        })
        if response.status_code == 200:
            print(
                f"   - register {service_type}: {service_name}, {service_url}")
        else:
            print(f"Failed to register {service_name}: {response.text}")

    service_types = [
        'dataset', 'model',
        'model_evaluation', 'xai',
        'xai_evaluation'
    ]

    for service_type in service_types:
        for service_name, service_url in services.get(service_type, {}).items():
            make_service_reg_request(
                central_url, service_url, service_name, service_type)


def configuration_operation_request(central_url, configuration, operation):
    def make_configuration_operation_request(url, type, config):
        configuration_name = config['name'] if config.get(
            'name') is not None else config[Configuration.configuration_name]
        configuration_content = config['content'] if config.get(
            'content') is not None else config[Configuration.configuration_content]
        data = {
            'act': operation,
            Configuration.configuration_name: configuration_name,
            Configuration.configuration_type: type,
            Configuration.configuration_content: configuration_content,
        }
        if config.get(Configuration.configuration_id) is not None:
            data[Configuration.configuration_id] = config[Configuration.configuration_id]

        # print_prety_json(data)
        response = requests.post(url, data=data)
        if response.status_code == 200:
            print(f"{operation} config {configuration_name} successfully")
        else:
            print(f"Failed to {operation} configuration: {response.text}")

    for dataset_config in configuration.get('dataset', []):
        make_configuration_operation_request(
            f"{central_url}/task_publisher/configuration", 'dataset', dataset_config)

    for model_config in configuration.get('model', []):
        make_configuration_operation_request(
            f"{central_url}/task_publisher/configuration", 'model', model_config)

    for trainer_config in configuration.get('trainer', []):
        make_configuration_operation_request(
            f"{central_url}/task_publisher/configuration", 'trainer', trainer_config)


def task_sheet_create_request(central_url, task_sheet_for_create):
    def make_task_sheet_create_request(
        url, type, task_sheet, service_info_list, configuration_list
    ):
        task_parameters = task_sheet.get('task_parameters', {})
        task_parameters['dataset_configuration_id'] = [
            get_id_by_name(
                dataset_config, configuration_list,
                Configuration.configuration_name, Configuration.configuration_id
            )
            for dataset_config in task_sheet.get('dataset_config', [])
        ]
        config_and_id_keys = [
            ('model_config', 'model_configuration_id'),
            ('trainer_config', 'trainer_configuration_id'),
        ]
        for config_key, id_key in config_and_id_keys:
            task_parameters[id_key] = get_id_by_name(
                task_sheet.get(config_key), configuration_list,
                Configuration.configuration_name, Configuration.configuration_id
            )

        data = dict(
            act='create',
            task_type=type,
            task_sheet_name=task_sheet['name'],
            task_function_key=task_sheet['task_function_key'],
            task_parameters=prety_print_json(task_parameters),
        )

        service_name_id_map = [
            ('db_service', 'db_service_executor_id'),
            ('model_service', 'model_service_executor_id'),
            ('model_evaluation_service', 'model_evaluation_service_executor_id'),
            ('xai_service', 'xai_service_executor_id'),
            ('xai_evaluation_service', 'xai_evaluation_service_executor_id'),
        ]

        for service_name_key, service_id_key in service_name_id_map:
            service_name = task_sheet.get(service_name_key)
            if service_name is not None:
                data[service_id_key] = get_id_by_name(
                    service_name, service_info_list,
                    ExecutorRegInfo.executor_name, ExecutorRegInfo.executor_id
                )

        previous_task_ticket = task_sheet.get('previous_task_ticket')
        if previous_task_ticket is not None:
            data['previous_task_ticket'] = previous_task_ticket

        response = requests.post(url, data=data)
        if response.status_code == 200:
            print(f"create task sheet {task_sheet['name']} successfully")
        else:
            print(f"Failed to apply task sheet: {response.text}")

    service_info_list = get_entity_list(central_url, "executor")
    configuration_list = get_entity_list(central_url, "configuration")

    task_sheet_types = ['training',
                        'model_evaluation', 'xai', 'xai_evaluation']
    for task_sheet_type in task_sheet_types:
        for task_sheet in task_sheet_for_create.get(task_sheet_type, []):
            make_task_sheet_create_request(
                f"{central_url}/task_publisher/task_sheet",
                task_sheet_type,
                task_sheet,
                service_info_list,
                configuration_list
            )


def pipeline_sheet_create_request(central_url, pipeline_sheet_for_create):
    def make_pipeline_sheet_create_request(
        url, type, pipeline_sheet, service_info_list
    ):
        data = dict(
            act='create',
            pipeline_type=type,
            pipeline_sheet_name=pipeline_sheet['name'],
        )

        task_sheet_name_key_and_id_key_map = [
            ('train', 'train_task_sheet_id'),
            ('model_evaluation', 'model_evaluation_task_sheet_id'),
            ('xai', 'xai_task_sheet_id'),
            ('xai_evaluation', 'xai_evaluation_task_sheet_id'),
        ]
        for task_sheet_name_key_and_id_key in task_sheet_name_key_and_id_key_map:
            task_sheet_name_key, task_sheet_id_key = task_sheet_name_key_and_id_key
            task_sheet_name = pipeline_sheet.get(task_sheet_name_key)
            if task_sheet_name is not None:
                data[task_sheet_id_key] = get_id_by_name(
                    task_sheet_name,
                    get_entity_list(central_url, "task_sheet"),
                    TaskSheet.task_sheet_name, TaskSheet.task_sheet_id
                )

        response = requests.post(url, data=data)
        if response.status_code == 200:
            print(
                f"create pipeline sheet {pipeline_sheet['name']} successfully")
        else:
            print(f"Failed to apply pipeline sheet: {response.text}")

    service_info_list = get_entity_list(central_url, "executor")
    pipeline_sheet_type_map = [
        'training_pipeline',
        'xai_pipeline',
        'xai_evaluation_pipeline',
        'training_xai_pipeline',
    ]
    for pipeline_sheet_type in pipeline_sheet_type_map:
        for pipeline_sheet in pipeline_sheet_for_create.get(pipeline_sheet_type, []):
            make_pipeline_sheet_create_request(
                f"{central_url}/task_publisher/pipeline_sheet",
                pipeline_sheet_type,
                pipeline_sheet,
                service_info_list
            )


def sheet_operation_request(central_url, sheet_type, sheet_name, operation, verbose=False):
    data = {
        'act': operation,
        f'{sheet_type}_id': get_id_by_name(
            sheet_name, get_entity_list(central_url, sheet_type),
            TaskSheet.task_sheet_name if sheet_type == 'task_sheet' else PipelineSheet.pipeline_sheet_name,
            TaskSheet.task_sheet_id if sheet_type == 'task_sheet' else PipelineSheet.pipeline_sheet_id
        ),
    }
    response = requests.post(
        f"{central_url}/task_publisher/{sheet_type}", data=data)
    if response.status_code == 200:
        if verbose:
            print(f"execute {sheet_type} sheet {sheet_name} successfully")
        return response.json()
    else:
        if verbose:
            print(f"Failed to execute {sheet_type} sheet: {response.text}")


def task_execution_operation_request(central_url, task_execution_id, operation):
    data = {
        'act': operation,
        'task_ticket': task_execution_id,
    }
    response = requests.post(
        f"{central_url}/task_publisher/task_execution", data=data)
    if response.status_code == 200:
        print(f"execute task execution {task_execution_id} successfully")
    else:
        print(f"Failed to execute task execution: {response.text}")


def get_execution_list(central_url, execution_type, sheet_name):
    data = {
        f"{execution_type.split('_')[0]}_sheet_id": get_id_by_name(
            sheet_name,
            get_entity_list(
                central_url, f"{execution_type.split('_')[0]}_sheet"),
            TaskSheet.task_sheet_name if execution_type == 'task_execution' else PipelineSheet.pipeline_sheet_name,
            TaskSheet.task_sheet_id if execution_type == 'task_execution' else PipelineSheet.pipeline_sheet_id
        )
    }
    response = requests.get(
        f"{central_url}/task_publisher/{execution_type}", params=data)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Failed to get {execution_type} list: {response.text}")
        return []


def check_exist_update_delete(
    existing_entity_list,
    planned_entities,
    entity_types,
    entity_id_key,
    entity_name_key,
    entity_type_key,
    entity_existance_check
):
    existing_entity_dict: dict = {
        entity[entity_name_key]: entity for entity in existing_entity_list}
    planned_entities_for_create: dict = dict()
    planned_entities_for_update: dict = dict()
    entities_for_delete: dict = dict()

    for entity_type in entity_types:
        planned_entities_for_create[entity_type] = []
        planned_entities_for_update[entity_type] = []
        entities_for_delete[entity_type] = []
    for entity_type in entity_types:
        for planned_entity in planned_entities.get(entity_type, []):
            existed_entity = existing_entity_dict.get(
                planned_entity['name'])
            if existed_entity is None:
                planned_entities_for_create[entity_type].append(
                    planned_entity)
            elif entity_existance_check(planned_entity, existed_entity):
                planned_entity[entity_id_key] = existed_entity[entity_id_key]
                planned_entities_for_update[entity_type].append(
                    planned_entity)

    for existed_entity in existing_entity_dict.values():
        entity_name = existed_entity[entity_name_key]
        entity_type = existed_entity[entity_type_key]
        if not any(item["name"] == entity_name for item in planned_entities.get(entity_type, [])):
            entities_for_delete[entity_type].append(
                existed_entity)

    return planned_entities_for_create, planned_entities_for_update, entities_for_delete


def print_plan(planned_entities_for_create, planned_entities_for_update, entities_for_delete):
    print('='*30, 'create', '='*30)
    print_prety_json(planned_entities_for_create)
    print('='*30, 'update', '='*30)
    print_prety_json(planned_entities_for_update)
    print('='*30, 'delete', '='*30)
    print_prety_json(entities_for_delete)
