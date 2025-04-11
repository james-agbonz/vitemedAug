from backend_central_dev.data_processing.mix.aug_base import *
import os
from backend_central_dev.data_processing.dataset_utils import (
    XEraseDataset,
    NewBasicDataModule,
    dataclass,
    field,
    Type,
)
import numpy as np
import pandas as pd

overall_num_classes = 19
original_dir = ["mimic-cxr", "png-208"]


@dataclass
class MIMICCxrDataset(XEraseDataset):

    num_classes: int = overall_num_classes
    data_dir: list[str] = field(default_factory=lambda: original_dir)
    head_classes_idx: tuple = (6, 12, 11, 3, 13, 9, 0, 1, 7, 8)
    medium_classes_idx: tuple = (17, 18, 10, 2, 4, 5)
    tail_classes_idx: tuple = (15, 16, 14)

    def __check_if_downloaded__(self):
        return os.path.exists(
            os.path.join(self.data_dir, "mimic-cxr-lt_single-label_train.csv")
        )

    def __download_data__(self):
        os.system(
            f"kaggle datasets download junhuang96/mimic-cxr-208-private -p {self.data_dir} --unzip"
        )

    def __check_if_saliency_map_downloaded__(self):
        return os.path.exists(
            os.path.join(
                self.saliency_map_data_dir, "mimic-cxr-lt_single-label_train.csv"
            )
        )

    def __download_saliency_map_data__(self):
        os.system(
            f"kaggle datasets download junhuang96/mimic-cxr-png-208-gag-30-06 -p {self.saliency_map_data_dir} --unzip"
        )

    def __x_y_pair_list__(self) -> np.ndarray | tuple:
        train_csv = pd.read_csv(
            os.path.join(self.data_dir, "mimic-cxr-lt_single-label_train.csv")
        )
        test_csv = pd.read_csv(
            os.path.join(self.data_dir, "mimic-cxr-lt_single-label_test.csv")
        )

        train_csv["label"] = train_csv.apply(
            lambda row: np.argmax(row.array[4:]), axis=1
        )
        test_csv["label"] = test_csv.apply(
            lambda row: np.argmax(row.array[4:]), axis=1)

        train_label_json = [
            [os.path.join(self.data_dir, t[0].replace(".jpg", ".png")), t[1]]
            for t in train_csv[["path", "label"]].to_numpy()
        ]

        test_label_json = [
            [os.path.join(self.data_dir, t[0].replace(".jpg", ".png")), t[1]]
            for t in test_csv[["path", "label"]].to_numpy()
        ]

        return np.array(train_label_json), np.array(test_label_json)

    def __sal_path_transfer__(self, img_path) -> str:
        # return img_path.replace("/jpg-224/", "/jpg-224-gag-30-06/")
        return img_path.replace("/png-208/", "/png-208-gag-30-06/")


@dataclass
class MIMICCxrDataModule(NewBasicDataModule):

    dataset_class: Type = MIMICCxrDataset
