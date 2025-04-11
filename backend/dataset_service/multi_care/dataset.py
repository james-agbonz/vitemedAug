import os
import json
from backend_central_dev.data_processing.dataset_utils import (
    XEraseDataset,
    NewBasicDataModule,
    dataclass,
    field,
    Type
)
import numpy as np
import pandas as pd
from IPython.display import display


overall_num_classes = -1
original_dir = ["multicare", "multicare_radiology_thorax_xray"]


@dataclass
class MultiCare_Thorax_XRay(XEraseDataset):

    num_classes: int = overall_num_classes
    data_dir: list[str] = field(default_factory=lambda: original_dir)
    task_type: str = "image-captioning"

    class_labels: tuple = ()

    def __check_if_downloaded__(self):
        # article_metadata_json_path = os.path.join(
        #     self.data_dir, "article_metadata.json"
        # )

        # article_metadata_json_df = pd.read_json(article_metadata_json_path)

        # case_report_citations_json_path = os.path.join(
        #     self.data_dir, "case_report_citations.json"
        # )
        # case_report_citations_json_df = pd.read_json(
        #     case_report_citations_json_path)

        cases_csv_path = os.path.join(self.data_dir, "cases.csv")
        # cases_csv_df = pd.read_csv(cases_csv_path)

        image_metadata_json_path = os.path.join(
            self.data_dir, "image_metadata.json"
        )
        image_metadata_json_df = pd.read_json(
            image_metadata_json_path, orient="records", lines=True)

        return os.path.exists(
            image_metadata_json_path
        )

    def __x_y_pair_list__(self) -> np.ndarray:
        pairs = []
        image_metadata_json_path = os.path.join(
            self.data_dir, "image_metadata.json"
        )
        image_metadata_json_df = pd.read_json(
            image_metadata_json_path, orient="records", lines=True)

        for i, row in image_metadata_json_df.iterrows():
            pairs.append((row["file_path"], row["caption"]))

        return np.array(pairs)


@dataclass
class MultiCare_Thorax_XRay_DataModule(NewBasicDataModule):

    dataset_class: Type = MultiCare_Thorax_XRay
