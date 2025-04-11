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
from IPython.display import display
import tqdm

overall_num_classes = 9
original_dir = ["isic", "full"]


@dataclass
class ISIC_MultiModal(XEraseDataset):

    num_classes: int = overall_num_classes
    data_dir: list[str] = field(default_factory=lambda: original_dir)
    class_labels: tuple = (
        "Melanoma",
        "Melanocytic nevus",
        "Basal cell carcinoma",
        "Actinic keratosis",
        "Benign keratosis (solar lentigo / seborrheic keratosis / lichen planus-like keratosis)",
        'Dermatofibroma',
        "Vascular lesion",
        "Squamous cell carcinoma",
        "None of the others"
    )

    def __check_if_downloaded__(self):
        d1 = os.path.exists(
            os.path.join(self.data_dir, "jpeg-melanoma-512x512", "train.csv")
        )
        d2 = os.path.exists(
            os.path.join(self.data_dir, "jpeg-isic2019-512x512", "train.csv")
        )
        return d1 and d2

    def __download_data__(self):
        os.system(
            f"kaggle datasets download cdeotte/jpeg-isic2019-512x512 -p {self.data_dir}/jpeg-isic2019-512x512 --unzip"
        )
        os.system(
            f"kaggle datasets download cdeotte/jpeg-melanoma-512x512 -p {self.data_dir}/jpeg-melanoma-512x512 --unzip"
        )

    def __x_y_pair_list__(self) -> np.ndarray:

        df, df_test, meta_features, n_meta_features, mel_idx = get_df(
            "9c_b4ns_448_ext_15ep-newfold",
            9,
            self.data_dir,
            512,
            False
        )
        fold = self.dataset_init_kwargs['fold']
        df_train = df[df['fold'] != fold]
        df_val = df[df['fold'] == fold]

        return np.array([(row['filepath'], row['target']) for i, row in df_train.iterrows()]), np.array([(row['filepath'], row['target']) for i, row in df_val.iterrows()])


@dataclass
class ISIC_MultiModal_DataModule(NewBasicDataModule):

    dataset_class: Type = ISIC_MultiModal
    mean_t: list[float] = field(default_factory=lambda: [0.485, 0.456, 0.406])
    std_t: list[float] = field(default_factory=lambda: [0.229, 0.224, 0.225])
    normalize: bool = True


def get_meta_data(df_train, df_test):

    # One-hot encoding of anatom_site_general_challenge feature
    concat = pd.concat([df_train['anatom_site_general_challenge'],
                       df_test['anatom_site_general_challenge']], ignore_index=True)
    dummies = pd.get_dummies(concat, dummy_na=True,
                             dtype=np.uint8, prefix='site')
    df_train = pd.concat([df_train, dummies.iloc[:df_train.shape[0]]], axis=1)
    df_test = pd.concat(
        [df_test, dummies.iloc[df_train.shape[0]:].reset_index(drop=True)], axis=1)
    # Sex features
    df_train['sex'] = df_train['sex'].map({'male': 1, 'female': 0})
    df_test['sex'] = df_test['sex'].map({'male': 1, 'female': 0})
    df_train['sex'] = df_train['sex'].fillna(-1)
    df_test['sex'] = df_test['sex'].fillna(-1)
    # Age features
    df_train['age_approx'] /= 90
    df_test['age_approx'] /= 90
    df_train['age_approx'] = df_train['age_approx'].fillna(0)
    df_test['age_approx'] = df_test['age_approx'].fillna(0)
    df_train['patient_id'] = df_train['patient_id'].fillna(0)
    # n_image per user
    df_train['n_images'] = df_train.patient_id.map(
        df_train.groupby(['patient_id']).image_name.count())
    df_test['n_images'] = df_test.patient_id.map(
        df_test.groupby(['patient_id']).image_name.count())
    df_train.loc[df_train['patient_id'] == -1, 'n_images'] = 1
    df_train['n_images'] = np.log1p(df_train['n_images'].values)
    df_test['n_images'] = np.log1p(df_test['n_images'].values)
    # image size
    train_images = df_train['filepath'].values
    train_sizes = np.zeros(train_images.shape[0])
    for i, img_path in enumerate(tqdm(train_images)):
        train_sizes[i] = os.path.getsize(img_path)
    df_train['image_size'] = np.log(train_sizes)
    test_images = df_test['filepath'].values
    test_sizes = np.zeros(test_images.shape[0])
    for i, img_path in enumerate(tqdm(test_images)):
        test_sizes[i] = os.path.getsize(img_path)
    df_test['image_size'] = np.log(test_sizes)

    meta_features = ['sex', 'age_approx', 'n_images', 'image_size'] + \
        [col for col in df_train.columns if col.startswith('site_')]
    n_meta_features = len(meta_features)

    return df_train, df_test, meta_features, n_meta_features


def get_df(kernel_type, out_dim, data_dir, data_folder, use_meta):

    # 2020 data
    df_train = pd.read_csv(os.path.join(
        data_dir, f'jpeg-melanoma-{data_folder}x{data_folder}', 'train.csv'))
    df_train = df_train[df_train['tfrecord'] != -1].reset_index(drop=True)
    df_train['filepath'] = df_train['image_name'].apply(lambda x: os.path.join(
        data_dir, f'jpeg-melanoma-{data_folder}x{data_folder}/train', f'{x}.jpg'))

    if 'newfold' in kernel_type:
        tfrecord2fold = {
            8: 0, 5: 0, 11: 0,
            7: 1, 0: 1, 6: 1,
            10: 2, 12: 2, 13: 2,
            9: 3, 1: 3, 3: 3,
            14: 4, 2: 4, 4: 4,
        }
    elif 'oldfold' in kernel_type:
        tfrecord2fold = {i: i % 5 for i in range(15)}
    else:
        tfrecord2fold = {
            2: 0, 4: 0, 5: 0,
            1: 1, 10: 1, 13: 1,
            0: 2, 9: 2, 12: 2,
            3: 3, 8: 3, 11: 3,
            6: 4, 7: 4, 14: 4,
        }
    df_train['fold'] = df_train['tfrecord'].map(tfrecord2fold)
    df_train['is_ext'] = 0

    # 2018, 2019 data (external data)
    df_train2 = pd.read_csv(os.path.join(
        data_dir, f'jpeg-isic2019-{data_folder}x{data_folder}', 'train.csv'))
    df_train2 = df_train2[df_train2['tfrecord'] >= 0].reset_index(drop=True)
    df_train2['filepath'] = df_train2['image_name'].apply(lambda x: os.path.join(
        data_dir, f'jpeg-isic2019-{data_folder}x{data_folder}/train', f'{x}.jpg'))
    if 'newfold' in kernel_type:
        df_train2['tfrecord'] = df_train2['tfrecord'] % 15
        df_train2['fold'] = df_train2['tfrecord'].map(tfrecord2fold)
    else:
        df_train2['fold'] = df_train2['tfrecord'] % 5
    df_train2['is_ext'] = 1

    # Preprocess Target
    df_train['diagnosis'] = df_train['diagnosis'].apply(
        lambda x: x.replace('seborrheic keratosis', 'BKL'))
    df_train['diagnosis'] = df_train['diagnosis'].apply(
        lambda x: x.replace('lichenoid keratosis', 'BKL'))
    df_train['diagnosis'] = df_train['diagnosis'].apply(
        lambda x: x.replace('solar lentigo', 'BKL'))
    df_train['diagnosis'] = df_train['diagnosis'].apply(
        lambda x: x.replace('lentigo NOS', 'BKL'))
    df_train['diagnosis'] = df_train['diagnosis'].apply(
        lambda x: x.replace('cafe-au-lait macule', 'unknown'))
    df_train['diagnosis'] = df_train['diagnosis'].apply(
        lambda x: x.replace('atypical melanocytic proliferation', 'unknown'))

    if out_dim == 9:
        df_train2['diagnosis'] = df_train2['diagnosis'].apply(
            lambda x: x.replace('NV', 'nevus'))
        df_train2['diagnosis'] = df_train2['diagnosis'].apply(
            lambda x: x.replace('MEL', 'melanoma'))
    elif out_dim == 4:
        df_train2['diagnosis'] = df_train2['diagnosis'].apply(
            lambda x: x.replace('NV', 'nevus'))
        df_train2['diagnosis'] = df_train2['diagnosis'].apply(
            lambda x: x.replace('MEL', 'melanoma'))
        df_train2['diagnosis'] = df_train2['diagnosis'].apply(
            lambda x: x.replace('DF', 'unknown'))
        df_train2['diagnosis'] = df_train2['diagnosis'].apply(
            lambda x: x.replace('AK', 'unknown'))
        df_train2['diagnosis'] = df_train2['diagnosis'].apply(
            lambda x: x.replace('SCC', 'unknown'))
        df_train2['diagnosis'] = df_train2['diagnosis'].apply(
            lambda x: x.replace('VASC', 'unknown'))
        df_train2['diagnosis'] = df_train2['diagnosis'].apply(
            lambda x: x.replace('BCC', 'unknown'))
    else:
        raise NotImplementedError()

    # concat train data
    df_train = pd.concat([df_train, df_train2]).reset_index(drop=True)

    # test data
    df_test = pd.read_csv(os.path.join(
        data_dir, f'jpeg-melanoma-{data_folder}x{data_folder}', 'test.csv'))
    df_test['filepath'] = df_test['image_name'].apply(lambda x: os.path.join(
        data_dir, f'jpeg-melanoma-{data_folder}x{data_folder}/test', f'{x}.jpg'))

    if use_meta:
        df_train, df_test, meta_features, n_meta_features = get_meta_data(
            df_train, df_test)
    else:
        meta_features = None
        n_meta_features = 0

    # class mapping
    # {'AK': 0, 'BCC': 1, 'BKL': 2, 'DF': 3, 'SCC': 4, 'VASC': 5,
    #  'melanoma': 6, 'nevus': 7, 'unknown': 8}
    diagnosis2idx = {d: idx for idx, d in enumerate(
        sorted(df_train.diagnosis.unique()))}
    df_train['target'] = df_train['diagnosis'].map(diagnosis2idx)
    mel_idx = diagnosis2idx['melanoma']

    return df_train, df_test, meta_features, n_meta_features, mel_idx
