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

overall_num_classes = 20
original_dir = ["lt_cxr8", "original"]


@dataclass
class LtCxr8Dataset(XEraseDataset):

    num_classes: int = overall_num_classes
    data_dir: list[str] = field(default_factory=lambda: original_dir)
    head_classes_idx: tuple = (8, 19, 0, 4, 10, 13, 9)
    medium_classes_idx: tuple = (11, 1, 6, 3, 17, 5, 12, 18, 2)
    tail_classes_idx: tuple = (15, 16, 14, 7)

    def __check_if_downloaded__(self):
        return os.path.exists(os.path.join(self.data_dir, "test_list.txt"))

    def __download_data__(self):
        os.system(
            f"kaggle datasets download junhuang96/lt-cxr8-private -p {self.data_dir} --unzip"
        )

    def __check_if_saliency_map_downloaded__(self):
        return os.path.exists(os.path.join(self.saliency_map_data_dir, "test_list.txt"))

    def __download_saliency_map_data__(self):
        os.system(
            f"kaggle datasets download junhuang96/lt-cxr8-gag-private -p {self.saliency_map_data_dir} --unzip"
        )

    def __x_y_pair_list__(self) -> np.ndarray:
        train_csv = pd.read_csv(
            os.path.join(
                self.data_dir, "LongTailCXR", "nih-cxr-lt_single-label_train.csv"
            )
        )
        test_csv = pd.read_csv(
            os.path.join(
                self.data_dir, "LongTailCXR", "nih-cxr-lt_single-label_test.csv"
            )
        )

        train_csv["label"] = train_csv.apply(
            lambda row: np.argmax(row.array[1:-1]), axis=1
        )
        test_csv["label"] = test_csv.apply(
            lambda row: np.argmax(row.array[1:-1]), axis=1
        )

        train_label_json = [
            [os.path.join(self.data_dir, "processed-images", t[0]), t[1]]
            for t in train_csv[["id", "label"]].to_numpy()
        ]

        test_label_json = [
            [os.path.join(self.data_dir, "processed-images", t[0]), t[1]]
            for t in test_csv[["id", "label"]].to_numpy()
        ]

        return np.array(train_label_json), np.array(test_label_json)

    def __sal_path_transfer__(self, img_path) -> str:
        return img_path


@dataclass
class LtCxr8DataModule(NewBasicDataModule):

    dataset_class: Type = LtCxr8Dataset
