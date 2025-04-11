import argparse
import yaml
from backend_central_dev.constant import *
import pandas as pd
from tabulate import tabulate
from mlxops_sdk_function import *


def sheet_commands(
    operation,
    action,
    central_url,
    sheet_config,
    sheet_config_name,
    sheet_entity_types,
    sheet_id_name_type_key
):
    sheet_type = 'task_sheet' if operation == 'ts' else 'pipeline_sheet'
    planned_sheets_for_create, \
        planned_sheets_for_update, \
        sheets_for_delete = check_exist_update_delete(
            get_entity_list(central_url, sheet_type),
            sheet_config,
            sheet_entity_types,
            *sheet_id_name_type_key,
            lambda planned_entity, existed_entity: planned_entity[
                'name'] == existed_entity[sheet_id_name_type_key[1]]
        )

    if action == 'plan':
        print_plan(
            planned_sheets_for_create,
            planned_sheets_for_update,
            sheets_for_delete
        )
    elif action == 'apply':
        if sheet_type == 'task_sheet':
            task_sheet_create_request(
                central_url, planned_sheets_for_create)
        elif sheet_type == 'pipeline_sheet':
            pipeline_sheet_create_request(
                central_url, planned_sheets_for_create)
    elif action in ['execute']:
        if sheet_config_name is None:
            print(
                f"{sheet_type} name is required (-{operation}_n or --{sheet_type}_name)")
            exit(1)
        else:
            sheet_operation_request(
                central_url,
                sheet_type,
                sheet_config_name,
                action
            )
    elif action == 'delete':
        print(f"Deleting {sheet_type} is not supported yet.")


def execution_commands(
    operation,
    action,
    sheet_config_name,
    execution_ticket_name,
    central_url,

):
    if action == 'list':
        if sheet_config_name is None:
            if operation == 'te':
                print("task_sheet name is required (-ts_n or --task_sheet_name)")
            elif operation == 'pe':
                print("pipeline_sheet name is required (-ps_n or --pipeline_sheet_name)")
            exit(1)
        else:
            tes = get_execution_list(
                central_url,
                "task_execution" if operation == 'te' else 'pipeline_execution',
                sheet_config_name
            )
            tes = [{k: v for k, v in te.items() if k in [
                TaskExecution.task_ticket if operation == 'te' else PipelineExecution.pipeline_ticket,
                TaskExecution.task_execution_name if operation == 'te' else PipelineExecution.pipeline_execution_name,
                TaskExecution.task_status,
            ]} for te in tes]

            df = pd.DataFrame(tes)
            if not df.empty:
                print(tabulate(df, headers='keys', tablefmt='pretty'))
            else:
                print(f"No executions found.")

    elif action == 'stop':
        if execution_ticket_name is None:
            if operation == 'te':
                print("task ticket is required (-tkt or --task_ticket)")
            elif operation == 'pe':
                print("pipeline ticket is required (-pkt or --pipeline_ticket)")
            exit(1)
        else:
            task_execution_operation_request(
                central_url,
                execution_ticket_name,
                action
            )
    elif action == 'delete':
        print(f"Deleting {operation} is not supported yet.")


def main():
    # Create the top-level parser
    parser = argparse.ArgumentParser(
        description='MLXOps SDK.')
    parser.add_argument(
        "-f", "--file", help="configuration file", required=True)

    operation = parser.add_subparsers(
        title='Operation', description='Operation to perform', dest='operation')
    operation.required = True

    parser_reg = operation.add_parser('reg', help='registration help')
    parser_config = operation.add_parser('config', help='configuration help')
    add_action_to_command(parser_config)

    parser_task_sheet = operation.add_parser('ts', help='task_sheet help')
    add_action_to_command(parser_task_sheet, choices=[
                          'apply', 'plan', 'execute', 'delete'])
    parser_task_sheet.add_argument(
        "-ts_n", "--task_sheet_name", help="task_sheet name", required=False
    )

    parser_task_execution = operation.add_parser(
        'te', help='task_execution help')
    add_action_to_command(parser_task_execution, choices=[
                          'list', 'stop', 'delete'])
    parser_task_execution.add_argument(
        "-ts_n", "--task_sheet_name", help="task_sheet name", required=False
    )
    parser_task_execution.add_argument(
        "-tkt", "--task_ticket", help="task ticket", required=False
    )

    parser_pipeline_sheet = operation.add_parser(
        'ps', help='pipeline_sheet help')
    add_action_to_command(parser_pipeline_sheet, choices=[
                          'apply', 'plan', 'execute'])
    parser_pipeline_sheet.add_argument(
        "-ps_n", "--pipeline_sheet_name", help="pipeline_sheet name", required=False
    )

    parser_pipeline_execution = operation.add_parser(
        'pe', help='pipeline_execution help')
    add_action_to_command(parser_pipeline_execution, choices=['list', 'stop'])
    parser_pipeline_execution.add_argument(
        "-ps_n", "--pipeline_sheet_name", help="pipeline_sheet name", required=False
    )
    parser_pipeline_execution.add_argument(
        "-pkt", "--pipeline_ticket", help="pipeline ticket", required=False
    )

    args = parser.parse_args()

    with open(args.file, 'r') as file:
        mlxops_config = yaml.safe_load(file)
        central_url = mlxops_config['central']

    if args.operation == 'reg':
        service_reg_request(central_url, mlxops_config['services'])

    elif args.operation == 'config':
        planned_configurations_for_create, \
            planned_configurations_for_update, \
            configurations_for_delete = check_exist_update_delete(
                get_entity_list(central_url, "configuration"),
                mlxops_config['configuration'],
                ['dataset', 'model', 'trainer'],
                Configuration.configuration_id,
                Configuration.configuration_name,
                Configuration.configuration_type,
                lambda planned_entity, existed_entity: planned_entity[
                    'content'] != existed_entity[Configuration.configuration_content]
            )

        if args.action == 'plan':
            print_plan(
                planned_configurations_for_create,
                planned_configurations_for_update,
                configurations_for_delete
            )
        elif args.action == 'apply':
            configuration_operation_request(
                central_url, planned_configurations_for_create, 'create')
            configuration_operation_request(
                central_url, planned_configurations_for_update, 'update')
            configuration_operation_request(
                central_url, configurations_for_delete, 'delete')

    elif args.operation == 'ts':
        sheet_commands(
            args.operation,
            args.action,
            central_url,
            mlxops_config['task_sheet'],
            args.task_sheet_name,
            [
                'training',
                'model_evaluation',
                'xai',
                'xai_evaluation'
            ],
            [
                TaskSheet.task_sheet_id,
                TaskSheet.task_sheet_name,
                TaskSheet.task_type
            ]
        )

    elif args.operation == 'ps':
        sheet_commands(
            args.operation,
            args.action,
            central_url,
            mlxops_config['pipeline_sheet'],
            args.pipeline_sheet_name,
            [
                'training_pipeline',
                'xai_pipeline',
                'xai_evaluation_pipeline',
                'training_xai_pipeline'
            ],
            [
                PipelineSheet.pipeline_sheet_id,
                PipelineSheet.pipeline_sheet_name,
                PipelineSheet.pipeline_type
            ]
        )

    elif args.operation == 'te':
        execution_commands(
            args.operation,
            args.action,
            args.task_sheet_name,
            args.task_ticket,
            central_url
        )
    elif args.operation == 'pe':
        execution_commands(
            args.operation,
            args.action,
            args.pipeline_sheet_name,
            args.pipeline_ticket,
            central_url
        )


if __name__ == '__main__':
    main()
