import asyncio
import os
import sys
import threading
from flask import Blueprint, Flask
import backend_central_dev.task_executor_blueprint as teb
import websockets
import websockets.asyncio
import websockets.asyncio.server

from backend_central_dev.task_publisher import TaskPublisher
try:
    from . import api
except:
    import api

bp, tp = None, None


async def ws_connection_handler(websocket: websockets.asyncio.server.ServerConnection):
    print(f"Ws connection: {websocket.request} on {websocket.local_address}")
    sec_ws_key = websocket.request.headers.get('Sec-WebSocket-Key')
    global tp
    tp.task_pipeline_manager.ws_map[sec_ws_key] = websocket
    # receive message from the ws
    async for message in websocket:
        # send message to that ws
        print(message)


async def main():
    print("Starting ws server")
    async with websockets.serve(ws_connection_handler, "0.0.0.0", 8765):
        await asyncio.get_running_loop().create_future()


def create_app(mode="dev") -> tuple[Flask, Blueprint, TaskPublisher]:
    def run():
        asyncio.run(main())
    if not sys.argv[-1] == "routes":
        threading.Thread(target=run).start()

    teb.load_env(mode)

    mongo_db_name = os.environ["MONGO_DB_NAME"]
    print(f"Mongo db name: {mongo_db_name}")

    global bp, tp
    bp, tp = api.init_central_blueprint_and_publisher()

    context_path = os.environ["CONTEXT_PATH"]
    static_url_path = context_path + "/static"

    app = Flask(
        'backend/central/main',
        instance_relative_config=True,
        static_url_path=static_url_path,
    )

    teb.set_app(app)

    app.register_blueprint(bp)
    app.config['SECRET_KEY'] = 'xaiops'
    return app
