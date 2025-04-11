from backend_central_dev.data_processing.mix.aug_base import *
import os
import json
from backend_central_dev.data_processing.dataset_utils import (
    XEraseDataset,
    NewBasicDataModule,
    dataclass,
    field,
    Type,
    download_and_extract,
)
import sys
import glob
import numpy as np
import pandas as pd

overall_num_classes = 8
original_dir = ["isic", "2019"]


@dataclass
class ISIC_2019_New(XEraseDataset):

    num_classes: int = overall_num_classes
    data_dir: list[str] = field(default_factory=lambda: original_dir)
    head_classes_idx: tuple = (1, 0, 2, 4)
    medium_classes_idx: tuple = (7, 3)
    tail_classes_idx: tuple = (6, 5)

    class_labels: tuple = (
        "Melanoma",
        "Melanocytic nevus",
        "Basal cell carcinoma",
        "Actinic keratosis",
        "Benign keratosis (solar lentigo / seborrheic keratosis / lichen planus-like keratosis)",
        'Dermatofibroma',
        "Vascular lesion",
        "Squamous cell carcinoma",
        # "None of the others"
    )

    def __check_if_downloaded__(self):
        return os.path.exists(
            os.path.join(self.data_dir, "ISIC_2019_Training_GroundTruth.csv")
        )

    def __download_data__(self):
        os.system(
            f"kaggle datasets download junhuang96/isic2019-private -p {self.data_dir} --unzip"
        )

    def __check_if_saliency_map_downloaded__(self):
        return os.path.exists(
            os.path.join(
                self.saliency_map_data_dir, "ISIC_2019_Training_GroundTruth.csv"
            )
        )

    def __x_y_pair_list__(self) -> np.ndarray:
        label_json = []
        csv_data = pd.read_csv(
            os.path.join(self.data_dir, "ISIC_2019_Training_GroundTruth.csv")
        )

        x = csv_data.to_numpy()[:, 0]
        y = csv_data.to_numpy()[:, 1:].argmax(axis=1)

        for i in range(len(x)):
            label_json.append(
                [
                    os.path.join(
                        self.data_dir, "ISIC_2019_Training_Input", x[i] + ".jpg"
                    ),
                    y[i],
                ]
            )

        return np.array(label_json)

    def __download_saliency_map_data__(self):
        os.system(
            f"kaggle datasets download junhuang96/isic-gag-30-06 -p {self.saliency_map_data_dir} --unzip"
        )

    def __sal_path_transfer__(self, img_path) -> str:
        return img_path.replace(".jpg", ".png")


@dataclass
class ISIC_2019_NewDataModule(NewBasicDataModule):

    dataset_class: Type = ISIC_2019_New
