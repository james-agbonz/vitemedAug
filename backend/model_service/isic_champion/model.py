

import pathlib
import os
from types import SimpleNamespace
from zipfile import ZipFile
import torch.nn as nn
import geffnet
import torch
from backend_central_dev.utils.pytorch_utils import get_device


def model_init_func(**model_init_kwargs):
    return ModelFx()


def model_fine_tune_func(model, output_features):
    return model


current_path = pathlib.Path(__file__).parent.resolve()


class ModelFx:

    def __init__(self, fold=0) -> None:
        device = get_device()
        args = SimpleNamespace()
        args.eval = 'best'
        args.kernel_type = '9c_b4ns_448_ext_15ep-newfold'
        args.model_dir = os.path.join(current_path, 'weights')
        args.enet_type = 'tf_efficientnet_b4_ns'
        args.n_meta_dim = '512,128'
        args.out_dim = 9

        if fold >= 0:
            if args.eval == 'best':
                model_file = \
                    os.path.join(args.model_dir,
                                 f'{args.kernel_type}_best_fold{fold}.pth')
            elif args.eval == 'best_20':
                model_file = os.path.join(
                    args.model_dir, f'{args.kernel_type}_best_20_fold{fold}.pth')
            if args.eval == 'final':
                model_file = os.path.join(
                    args.model_dir, f'{args.kernel_type}_final_fold{fold}.pth')

        if not os.path.exists(model_file):
            file_name = os.path.basename(model_file)
            dir_name = os.path.dirname(model_file)
            print(f"Downloading {file_name} to {dir_name}")
            os.system(
                f"kaggle datasets download boliu0/melanoma-winning-models -f {file_name} -p {dir_name} --unzip"
            )
            zip_path = os.path.join(dir_name, f"{file_name}.zip")
            with ZipFile(zip_path, "r") as zObject:
                zObject.extractall(path=dir_name)
                try:
                    os.remove(zip_path)
                except Exception as e:
                    print(f"Fire: {zip_path} might be removed already")

        if 'efficientnet' in args.enet_type:
            ModelClass = Effnet_Melanoma
        else:
            raise NotImplementedError()
        model = ModelClass(
            args.enet_type,
            n_meta_features=0,
            n_meta_dim=[int(nd) for nd in args.n_meta_dim.split(',')],
            out_dim=args.out_dim
        )
        model = model.to(device)
        if fold >= 0:
            try:  # single GPU model_file
                model.load_state_dict(torch.load(
                    model_file, map_location=device), strict=True)
            except:  # multi GPU model_file
                state_dict = torch.load(
                    model_file, map_location=device)
                state_dict = {k[7:] if k.startswith(
                    'module.') else k: state_dict[k] for k in state_dict.keys()}
                model.load_state_dict(state_dict, strict=True)

        model.eval()
        self.model = model

    def __call__(self, image):
        return self.model(image)


class Effnet_Melanoma(nn.Module):
    def __init__(self, enet_type, out_dim, n_meta_features=0, n_meta_dim=[512, 128], pretrained=False):
        super(Effnet_Melanoma, self).__init__()
        self.n_meta_features = n_meta_features
        self.enet = geffnet.create_model(enet_type, pretrained=pretrained)
        self.dropouts = nn.ModuleList([
            nn.Dropout(0.5) for _ in range(5)
        ])
        in_ch = self.enet.classifier.in_features
        if n_meta_features > 0:
            self.meta = nn.Sequential(
                nn.Linear(n_meta_features, n_meta_dim[0]),
                nn.BatchNorm1d(n_meta_dim[0]),
                Swish_Module(),
                nn.Dropout(p=0.3),
                nn.Linear(n_meta_dim[0], n_meta_dim[1]),
                nn.BatchNorm1d(n_meta_dim[1]),
                Swish_Module(),
            )
            in_ch += n_meta_dim[1]
        self.myfc = nn.Linear(in_ch, out_dim)
        self.enet.classifier = nn.Identity()

    def extract(self, x):
        x = self.enet(x)
        return x

    def forward(self, x, x_meta=None):
        x = self.extract(x).squeeze(-1).squeeze(-1)
        if self.n_meta_features > 0:
            x_meta = self.meta(x_meta)
            x = torch.cat((x, x_meta), dim=1)
        for i, dropout in enumerate(self.dropouts):
            if i == 0:
                out = self.myfc(dropout(x))
            else:
                out += self.myfc(dropout(x))
        out /= len(self.dropouts)
        return out


sigmoid = nn.Sigmoid()


class Swish(torch.autograd.Function):
    @staticmethod
    def forward(ctx, i):
        result = i * sigmoid(i)
        ctx.save_for_backward(i)
        return result

    @staticmethod
    def backward(ctx, grad_output):
        i = ctx.saved_variables[0]
        sigmoid_i = sigmoid(i)
        return grad_output * (sigmoid_i * (1 + i * (1 - sigmoid_i)))


class Swish_Module(nn.Module):
    def forward(self, x):
        return Swish.apply(x)
