# autopep8: off
import torch.nn.functional as F
from torchvision import transforms
from lime import lime_image
import shap
from pytorch_grad_cam import GradCAM
from pytorch_grad_cam.utils.model_targets import ClassifierOutputTarget
import sys
import os

import torch

sys.path.insert(0, os.path.join(os.path.dirname(__file__)))
import gradient_methods
from backend_central_dev.xai.xai_task import task_wrapper
from backend_central_dev.utils import data_utils
# autopep8: on


def Guided_AbsoluteGrad_xai(task_ticket, publisher_endpoint_url, task_parameters):
    return task_wrapper(
        task_ticket, publisher_endpoint_url,
        task_parameters, gradient_methods.guided_absolute_grad
    )


def vanillagrad_xai(task_ticket, publisher_endpoint_url, task_parameters):
    print(task_ticket, publisher_endpoint_url, task_parameters)
    ...


def smoothgrad_xai(task_ticket, publisher_endpoint_url, task_parameters):
    print(task_ticket, publisher_endpoint_url, task_parameters)
    ...


def vargrad_xai(task_ticket, publisher_endpoint_url, task_parameters):
    print(task_ticket, publisher_endpoint_url, task_parameters)
    ...


def ig_xai(task_ticket, publisher_endpoint_url, task_parameters):
    print(task_ticket, publisher_endpoint_url, task_parameters)
    ...


def gig_xai(task_ticket, publisher_endpoint_url, task_parameters):
    print(task_ticket, publisher_endpoint_url, task_parameters)
    ...


def bg_xai(task_ticket, publisher_endpoint_url, task_parameters):
    print(task_ticket, publisher_endpoint_url, task_parameters)
    ...


def big_xai(task_ticket, publisher_endpoint_url, task_parameters):
    print(task_ticket, publisher_endpoint_url, task_parameters)
    ...


cam_objs = []


def grad_cam(model: torch.nn.Module, images: torch.Tensor, targets: torch.Tensor,
             target_layers=None, **kwargs):
    cam = None
    for c in cam_objs:
        if c['model'] == model and c['target_layers']:
            cam = c['cam']
    if cam is None:
        cam = GradCAM(model=model, target_layers=target_layers)
        cam_objs.append({
            'model': model,
            'target_layers': target_layers,
            'cam': cam
        })

    targets = [ClassifierOutputTarget(i.item()) for i in targets]
    # st = time.time()
    grayscale_cam = cam(input_tensor=images, targets=targets, **kwargs)
    # et = time.time() - st
    # print(et)
    n, w, h = grayscale_cam.shape
    # grayscale_cam = grayscale_cam.reshape(n, 1, w, h)
    # print(grayscale_cam.shape)
    return data_utils.min_max_norm_matrix(torch.tensor(grayscale_cam, device=images.device, dtype=images.dtype))


def shap_map(
    model: torch.nn.Module,
    images: torch.Tensor,
    targets: torch.Tensor,
    image_processor,
    masker_params: tuple,
    device,
    shap_params: dict = {},
    denorm: bool = True,
    norm_output=True
):
    actual_shap_params = dict(
        max_evals=100,
        batch_size=10,
        silent=True
    )
    for k, v in shap_params.items():
        actual_shap_params[k] = v

    def f(x):
        # print(x.shape, type(x), x.dtype)
        t = torch.tensor(x.copy().transpose(0, 3, 1, 2), device=device)
        # print(t.shape, type(t), t.dtype)
        out = model(t)
        # print("out:", out.shape)
        return out.cpu().detach().numpy()

    explainer = shap.Explainer(f, shap.maskers.Image(*masker_params))

    actual_shap_params['outputs'] = shap.Explanation.argsort.flip[:1]
    shap_value = explainer(
        image_processor(data_utils.denormm_i_t(images)
                        ) if denorm else image_processor(images),
        **actual_shap_params
    )

    rs = torch.tensor(shap_value.values[:, :, :, 0, 0]).float()

    return data_utils.min_max_norm_matrix(rs) if norm_output else rs


def lime_map(
    model: torch.nn.Module,
    images: torch.Tensor,
    targets: torch.Tensor,
    device,
    denorm: bool = True,
    lime_params: dict = {},
    maks_params: dict = dict(
        positive_only=True,
        num_features=5,
        hide_rest=False
    ),
    norm_output=True
):
    actual_lime_params = dict(
        top_labels=5,
        hide_color=0,
        num_samples=100,
        batch_size=50,
        random_seed=42,
        progress_bar=False,
    )
    for k, v in lime_params.items():
        actual_lime_params[k] = v

    def f(x):
        transf = transforms.Compose([
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406],
                                 std=[0.229, 0.224, 0.225])
        ])
        batch = torch.stack(tuple(transf(i)
                            for i in x), dim=0).to(device)

        logits = model(batch)
        probs = F.softmax(logits, dim=1)
        return probs.detach().cpu().numpy()

    explainer = lime_image.LimeImageExplainer(
        # verbose=True,
        random_state=actual_lime_params['random_seed']
    )
    explanations = []
    images = data_utils.denormm_i_t(images) if denorm else images
    images = images.cpu().numpy()
    for image in images:
        explanation = explainer.explain_instance(
            image.transpose(1, 2, 0),
            # x[:4].cpu().numpy()[0].transpose(1, 2, 0),
            f,
            **actual_lime_params
        )
        temp, mask = explanation.get_image_and_mask(
            explanation.top_labels[0],
            **maks_params
        )
        explanations.append(mask)

    rs = torch.tensor(explanations).float()
    return data_utils.min_max_norm_matrix(rs) if norm_output else rs
