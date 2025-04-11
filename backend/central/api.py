import threading
import time
from flask import Blueprint, request, jsonify, make_response, current_app
from backend_central_dev.constant import *
import json
from backend_central_dev.utils.module_utils import filter_form_data_params_by_module
from backend_central_dev.task_publisher import TaskPublisher
from backend_central_dev.entity.WsMessage import *
from backend_central_dev.utils import provenence_utils
# from prov.dot import prov_to_dot


def init_central_blueprint_and_publisher():
    bp = Blueprint("central", __name__, url_prefix="/task_publisher")

    task_publisher_name = "central"
    tp = TaskPublisher(
        task_publisher_name,
        component_path=__file__,
        import_name=__name__,
        context_path="/task_publisher",
    )

    @bp.errorhandler(400)
    def bad_request_error(error):
        response = {
            "error": "Bad Request",
            "description": error.description,
            "method": request.method,
            "url": request.url
        }
        return jsonify(response), 400

    @bp.route("/executor", methods=["GET", "POST"])
    def executor():
        if request.method == "GET":
            return jsonify(tp.get_executor_registration_info())
        else:
            # executor register
            form_data = request.form
            act = form_data["act"]
            executor_endpoint_url = form_data[ExecutorRegInfo.executor_endpoint_url]
            if act == "create":
                executor_name = form_data[ExecutorRegInfo.executor_name]
                executor_type = form_data[ExecutorRegInfo.executor_type]
                exector_info = json.loads(
                    form_data[ExecutorRegInfo.executor_info])
                # publisher_endpoint_url = form_data['publisher_endpoint_url']
                exector_id = tp.register_executor_endpoint(
                    executor_name, executor_type, executor_endpoint_url, exector_info
                )
                return jsonify({"executor_id": exector_id})
            if act == "update":
                executor_id = form_data[ExecutorRegInfo.executor_id]
                exector_info = json.loads(
                    form_data[ExecutorRegInfo.executor_info])
                # publisher_endpoint_url = form_data['publisher_endpoint_url']
                exector_id = tp.update_executor_endpoint(
                    executor_id, executor_endpoint_url, exector_info
                )
                return jsonify({"executor_id": exector_id})

            if act == "delete":
                executor_id = form_data[ExecutorRegInfo.executor_id]
                tp.delete_executor_endpoint(executor_id)
                return ""

    @bp.route("/pipeline_execution", methods=["GET", "POST"])
    def pipeline_execution():
        if request.method == "GET":
            pipeline_sheet_id = request.args.get(
                PipelineSheet.pipeline_sheet_id)
            rs = tp.task_pipeline_manager.get_pipeline_executions_by_pipeline_sheet_id(
                pipeline_sheet_id)
            return jsonify(rs)
        else:
            form_data = request.form
            act = form_data["act"]
            if act == 'create':
                pipeline_sheet_id = form_data["pipeline_sheet_id"]
                pipeline_task_executions, pipeline_execution = \
                    tp.task_pipeline_manager.generate_pipeline_execution_from_pipeline_sheet(
                        tp.task_pipeline_manager.get_pipeline(pipeline_sheet_id)[0])
                return jsonify(pipeline_execution)

            if act == 'execute':
                pipeline_ticket = form_data["pipeline_ticket"]
                pipeline_execution = tp.task_pipeline_manager.get_pipeline_execution_by_ticket(
                    pipeline_ticket)
                task_execution = tp.get_task_execution(
                    pipeline_execution[PipelineExecution.task_execution_tickets][0])
                tp.task_pipeline_manager.tell_executor_to_execute_task(
                    task_execution, pipeline_ticket)

            if act == "delete":
                pipeline_ticket = form_data[PipelineExecution.pipeline_ticket]
                tp.task_pipeline_manager.delete_pipeline_execution(
                    pipeline_ticket)
            if act == "stop":
                pipeline_ticket = form_data[PipelineExecution.pipeline_ticket]
                tp.task_pipeline_manager.stop_pipeline_execution(
                    pipeline_ticket)
        return ""

    @bp.route("/pipeline_execution_result", methods=["GET"])
    async def pipeline_execution_result():
        pipeline_ticket = request.args.get("pipeline_ticket")
        act = request.args.get("act")

        if act == 'start_ws_stream':
            tp.pipeline_execution_result_streaming[pipeline_ticket] = True
            await send_pipeline_execution_result_with_ws(pipeline_ticket)
            return "Got it. Please receive the result!"

        if act == 'stop_ws_stream' and pipeline_ticket in tp.pipeline_execution_result_streaming:
            tp.pipeline_execution_result_streaming.pop(pipeline_ticket)
            return "Got it. Stop sending the result!"

    async def send_pipeline_execution_result_with_ws(pipeline_ticket):
        while True and tp.pipeline_execution_result_streaming.get(pipeline_ticket, False):
            hasRunning, pipeline_execution_presentations = tp.task_pipeline_manager.get_pipeline_execution_presentations(
                pipeline_ticket)
            await send_and_remove_closed(tp.task_pipeline_manager.ws_map, WsMessage(
                message_type=WsMessageType.PIPELINE_EXE_RESULT_UPDATE,
                payload=dict(
                    pipeline_ticket=pipeline_ticket,
                    result=pipeline_execution_presentations
                )
            ))

            if not hasRunning:
                break
            time.sleep(1)

    @bp.route("/pipeline_sheet", methods=["GET", "POST"])
    async def pipeline_sheet():
        if request.method == "GET":
            pipeline_sheet_id = request.args.get(
                PipelineSheet.pipeline_sheet_id)
            rs = tp.task_pipeline_manager.get_pipeline(pipeline_sheet_id)
            return jsonify(rs)
        else:
            form_data = request.form
            act = form_data["act"]
            form_data_pipeline_sheet_info = filter_form_data_params_by_module(
                form_data, PipelineSheet)
            if act == "create":
                return jsonify(tp.task_pipeline_manager.create_pipeline_sheet(form_data_pipeline_sheet_info))
            if act == "execute":
                if len(form_data_pipeline_sheet_info.keys()) == 1 and PipelineSheet.pipeline_sheet_id in form_data_pipeline_sheet_info:
                    form_data_pipeline_sheet_info = tp.task_pipeline_manager.get_pipeline(
                        form_data_pipeline_sheet_info[PipelineSheet.pipeline_sheet_id])[0]
                print(form_data_pipeline_sheet_info)
                pipeline_execution = await tp.task_pipeline_manager\
                    .execute_pipeline(form_data_pipeline_sheet_info)
                return jsonify(pipeline_execution)

            if act == "duplicate":
                pipeline_sheet_id = form_data[PipelineSheet.pipeline_sheet_id]
                pipeline_info = tp.task_pipeline_manager.duplicate_pipeline(
                    pipeline_sheet_id)
                return jsonify(pipeline_info)

            if act == "delete":
                # TODO: unable to delete when tasks are not deleted
                pipeline_sheet_id = form_data[PipelineSheet.pipeline_sheet_id]
                tp.task_pipeline_manager.delete_pipeline(pipeline_sheet_id)

            return ""

    @bp.route("/task_sheet", methods=["GET", "POST"])
    async def task_sheet():
        if request.method == "GET":
            task_sheet_ids = request.args.get("task_sheet_ids")
            if task_sheet_ids != None:
                task_sheet_ids = json.loads(task_sheet_ids)
            rs = tp.task_pipeline_manager.get_task_sheets(task_sheet_ids)
            return jsonify(rs)
        else:
            form_data = request.form
            act = form_data["act"]
            form_data_task_sheet = filter_form_data_params_by_module(
                form_data, TaskSheet)
            if act == "create":
                task_sheet_id = tp.task_pipeline_manager.create_task_sheet(
                    form_data_task_sheet)
                return jsonify({"task_sheet_id": task_sheet_id})
            if act == "execute":
                task_sheet_id = form_data[TaskSheet.task_sheet_id]
                task_ticket = await tp.task_pipeline_manager.execute_task_sheet_directly(task_sheet_id)
                return jsonify({"task_ticket": task_ticket})
            if act == "delete":
                # TODO: unable to delete when tasks are not deleted
                task_sheet_id = form_data[TaskSheet.task_sheet_id]
                tp.task_pipeline_manager.delete_task_sheet(task_sheet_id)
                return ""

    @bp.route("/task_execution", methods=["GET", "POST"])
    async def task():
        if request.method == "GET":
            # request a task info
            task_ticket = request.args.get(TaskExecution.task_ticket)
            if task_ticket != None:
                return jsonify(tp.get_task_execution(task_ticket))

            task_sheet_id = request.args.get(TaskSheet.task_sheet_id)
            if task_sheet_id != None:
                return jsonify(tp.get_task_executions_by_task_sheet_id(task_sheet_id))

            executor_id = request.args.get(TaskExecution.executor_id)
            task_type = request.args.get(TaskExecution.task_type)

            if executor_id != None and task_type != None:
                return jsonify(tp.get_task_executions_by_executor_id_and_task_type(
                    executor_id, task_type))

            return jsonify(tp.get_all_task())
        else:
            form_data = request.form
            act = form_data["act"]
            if act == 'create':
                task_sheet_id = form_data["task_sheet_id"]
                task_execution = tp.gen_task_execution(
                    tp.task_pipeline_manager.get_task_sheets([task_sheet_id])[0])
                return jsonify(task_execution)
            if act == 'execute':
                task_ticket = form_data["task_ticket"]
                task_execution = tp.get_task_execution(task_ticket)
                tp.task_pipeline_manager.tell_executor_to_execute_task(
                    task_execution)
            if act == "stop":
                task_ticket = form_data["task_ticket"]
                tp.task_pipeline_manager.stop_a_task(task_ticket)
            if act == "delete":
                task_ticket = form_data["task_ticket"]
                tp.task_pipeline_manager.delete_task(task_ticket)
            if act == "update_task_status":
                task_ticket = form_data[TaskExecution.task_ticket]
                task_status = form_data[TaskExecution.task_status]
                code_version_hash = form_data.get(
                    TaskExecution.code_version_hash, None)
                running_info = form_data[TaskExecution.running_info]
                pipeline_ticket = form_data.get(
                    PipelineExecution.pipeline_ticket)
                await tp.task_pipeline_manager.update_task_status(
                    task_ticket, task_status, code_version_hash, json.loads(
                        running_info), pipeline_ticket
                )

            return ""

    @bp.route("/task_execution_result", methods=["GET"])
    async def task_execution_result():
        task_ticket = request.args.get("task_ticket")
        act = request.args.get("act")
        if act == 'download':
            executor_info = tp.get_executor_registration_info(
                tp.get_task_execution(task_ticket)[TaskExecution.executor_id]
            )
            return f"{executor_info[ExecutorRegInfo.executor_endpoint_url]}/task_execution_result?task_ticket={task_ticket}"

        if act == 'start_ws_stream':
            # use ws to send the result
            tp.pipeline_execution_result_streaming[task_ticket] = True
            await send_task_execution_result_with_ws(task_ticket)
            return "Got it. Please receive the result!"

        if act == 'stop_ws_stream' and task_ticket in tp.pipeline_execution_result_streaming:
            tp.pipeline_execution_result_streaming.pop(task_ticket)
            return "Got it. Stop sending the result!"

    async def send_task_execution_result_with_ws(task_ticket):
        while True and tp.pipeline_execution_result_streaming.get(task_ticket, False):
            task_execution = tp.get_task_execution(task_ticket)
            await send_and_remove_closed(tp.task_pipeline_manager.ws_map, WsMessage(
                message_type=WsMessageType.TASK_EXE_RESULT_UPDATE,
                payload=dict(
                    task_ticket=task_ticket,
                    result=[
                        tp.task_pipeline_manager.get_task_execution_presentation(task_ticket, task_execution)]
                )
            ))
            if task_execution[TaskExecution.task_status] != TaskStatus.running:
                break
            time.sleep(1)

    @bp.route("/task_execution_std", methods=["GET"])
    def task_execution_std():
        task_ticket = request.args.get("task_ticket")
        return jsonify(tp.task_pipeline_manager.get_task_execution_std_out_and_err(task_ticket))

    @bp.route("/executor_task_function_key", methods=["GET"])
    def executor_task_function_key():
        executor_id = request.args.get(ExecutorRegInfo.executor_id)
        return jsonify(tp.task_pipeline_manager.get_task_executor_task_function_key(executor_id))

    @bp.route("/provenance", methods=["GET", "POST"])
    def provenance():
        if request.method == "GET":
            prov_type = request.args.get("prov_type")
            prov_raw = tp.get_provenance()
            if prov_type is None:
                return jsonify(prov_raw)
            else:
                prov_d = provenence_utils.provn(prov_raw)
                # dot = prov_to_dot(prov_d)
                # dot.write_png('article-prov.png')
                content_type = "text/provenance-notation"
                if prov_type == "provn":
                    resp_str = prov_d.get_provn()
                elif prov_type == "json":
                    resp_str = prov_d.serialize(indent=2)
                    content_type = "application/json"

            resp = make_response(resp_str)
            resp.headers['Content-Type'] = content_type
            return resp

    @bp.route("/predict_and_explain", methods=["POST"])
    def predict_and_explain():
        if request.method == 'POST':
            form_data = request.form
            image = request.files['image']
            model_service_executor_id = form_data[TaskSheet.model_service_executor_id]
            model_training_execution_ticket = form_data['model_training_execution_ticket']
            xai_service_executor_id = form_data[TaskSheet.xai_service_executor_id]
            xai_task_function_key = form_data['xai_task_function_key']
            return jsonify(tp.task_pipeline_manager.predict_and_explain(
                image, model_service_executor_id, model_training_execution_ticket,
                xai_service_executor_id, xai_task_function_key))

    @bp.route("/configuration", methods=["GET", "POST"])
    def configuration():
        if request.method == "GET":
            return jsonify(tp.get_configuration(
                configuration_id=request.args.get('configuration_id'))
            )
        else:
            # executor register
            form_data = request.form
            act = form_data["act"]
            if act == "create":
                payload = dict(form_data)
                return jsonify({"configuration_id": tp.create_configuration(payload)})
            if act == "update":
                payload = dict(form_data)
                return jsonify(tp.update_configuration(payload[Configuration.configuration_id], payload[Configuration.configuration_content]))
            if act == "delete":
                tp.delete_configuration(
                    form_data[Configuration.configuration_id])
                return ""

    @bp.route("/emission", methods=["GET", "POST"])
    def emission():
        if request.method == "GET":
            # return jsonify(tp.get_configuration(
            #     configuration_id=request.args.get('configuration_id'))
            # )
            return ""
        else:
            tp.save_task_emission(request.json)
            return ""
            # {'timestamp': '2024-12-02T01:15:37', 'project_name': 'VpDitjb8BYhhUQe.8G2BI3QZAF',
            # 'run_id': 'ca4c27eb-55d4-4304-8a33-b55b876dbe6f',
            # 'experiment_id': '5b0fa12a-3dd7-45bb-9766-cc326314d9f1',
            # 'duration': 6.873012375086546, 'emissions': 2.261949513906858e-09,
            # 'emissions_rate': 3.291059859147097e-10, 'cpu_power': 6.992900000000001,
            # 'gpu_power': 0.6223000000000001, 'ram_power': 0.13530921936035156,
            # 'cpu_energy': 3.3799251506155514e-07, 'gpu_energy': 6.074734936716398e-07,
            # 'ram_energy': 6.0449174601617805e-09, 'energy_consumed': 9.515109261933568e-07,
            # 'country_name': 'Canada', 'country_iso_code': 'CAN', 'region': 'quebec',
            # 'cloud_provider': '', 'cloud_region': '', 'os': 'macOS-14.2.1-arm64-arm-64bit',
            # 'python_version': '3.11.4', 'codecarbon_version': '2.8.0',
            # 'cpu_count': 10, 'cpu_model': 'Apple M1 Max', 'gpu_count': 1,
            # 'gpu_model': 'Apple M1 Max', 'longitude': -73.574, 'latitude': 45.4893,
            # 'ram_total_size': 32.0, 'tracking_mode': 'process', 'on_cloud': 'N',
            # 'pue': 1.0, 'user': 'yinnnyou'}

    return bp, tp
