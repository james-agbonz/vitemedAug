import torch.nn as nn
from torchvision import models
from backend_central_dev.model_training.lightning_model import FineTunableModel


# def pytorch_resnet_fine_tuning(model, output_features):
#     num_ftrs = model.fc.in_features
#     model.fc = nn.Linear(num_ftrs, output_features)
#     return model


# def pytorch_efficientnet_fine_tuning(model, output_features):
#     in_features = model.classifier[-1].in_features
#     model.classifier[-1] = nn.Linear(
#         in_features=in_features, out_features=output_features
#     )
#     return model


# fine_tunable_model = FineTunableModel(
#     model_init_func=lambda: models.efficientnet_v2_s(
#         weights=models.EfficientNet_V2_S_Weights.IMAGENET1K_V1),
#     model_fine_tune_func=pytorch_efficientnet_fine_tuning
# )

def model_init_func():
    return models.efficientnet_v2_s(
        weights=models.EfficientNet_V2_S_Weights.IMAGENET1K_V1
    )


def model_fine_tune_func(model, output_features):
    in_features = model.classifier[-1].in_features
    model.classifier[-1] = nn.Linear(
        in_features=in_features, out_features=output_features
    )
    return model
