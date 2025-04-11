import os
import sys

from backend_central_dev.task_executor_blueprint import (
    ExecutorBluePrint, create_service
)
ebp = ExecutorBluePrint(
    "vision_encoder_decoder", __name__, component_path=__file__, url_prefix="/vision_encoder_decoder"
)
app = create_service(ebp)
