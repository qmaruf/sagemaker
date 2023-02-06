import tarfile
from sklearn.metrics import classification_report
import gzip
import pickle
from pathlib import Path
import xgboost as xgb
from typing import Tuple
import boto3
from config import Config


s3session = boto3.client("s3")

def get_data() -> Tuple:
    """Download the mnist dataset from aws s3 and return the training, validation 
    and test sets

    Returns:
        Tuple: A tuple containing training, validation and test set features and labels 
        from the mnist dataset.
    """
    buffer = s3session.get_object(
        Bucket="sagemaker-sample-files",
        Key="datasets/image/MNIST/mnist.pkl.gz"
    )["Body"].read()

    decomp_buffer = gzip.decompress(buffer)
    train_set, valid_set, test_set = pickle.loads(
        decomp_buffer, encoding="latin1"
    )

    train_X, train_y = train_set
    valid_X, valid_y = valid_set
    test_X, test_y = test_set

    return train_X, train_y, valid_X, valid_y, test_X, test_y


def train_xgboost_model(model_path: Path) -> None:
    """Train a xgboost model on the mnist dataset and save it to the specified path.
    zip the model as model.tar.gz for sagemaker deployment.

    Args:
        model_path (Path): path to save the model.
    """

    train_X, train_y, valid_X, valid_y, test_X, test_y = get_data()
    clf = xgb.XGBClassifier(
        max_depth=1,
        learning_rate=0.2,
        n_estimators=2,
        objective="multi:softmax"
    )
    clf.fit(train_X, train_y,
            eval_set=[(valid_X, valid_y)],
            verbose=True
            )
    pred_y = clf.predict(test_X)
    clf_report = classification_report(test_y, pred_y)
    print(clf_report)

    clf.save_model(str(model_path))

    tar = tarfile.open(Config.model_tar, "w|gz")
    tar.add(model_path, arcname=model_path.name)
    tar.close()


if __name__ == "__main__":
    train_xgboost_model(Path(Config.model_path))
