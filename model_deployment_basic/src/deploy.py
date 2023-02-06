from typing import Dict
from config import Config
from pathlib import Path
import boto3
from loguru import logger
import sagemaker
import time

session = boto3.Session(profile_name="dev")
sm_client = session.client("sagemaker")
iam = session.client("iam")
role = iam.get_role(RoleName="SageMakerExecutionRole")["Role"]["Arn"]

def upload_model_to_s3(model_path: Path) -> str:
    """Get the trained model from model_path and upload to s3.

    Args:
        model_path (Path): model location (tar file)
    """
    s3 = session.client("s3")
    s3.upload_file(
        str(model_path),
        Config.bucket,
        Config.key
    )
    model_url = f"https://s3-{Config.region}.amazonaws.com/{Config.bucket}/{Config.key}"
    logger.info(f"Model uploaded from {model_path} to {model_url}")
    return model_url


def get_primary_container(model_url: str) -> Dict:
    container = sagemaker.image_uris.retrieve(
        "xgboost", Config.region, "1.5-1"
    )
    logger.info(f"Primary container path {container}")
    ret = {
        "Image": container,
        "ModelDataUrl": model_url
    }
    return ret

def create_model(primary_container: Dict):
    create_model_response = sm_client.create_model(
        ModelName=Config.model_name,
        ExecutionRoleArn=role,
        PrimaryContainer=primary_container
    )
    logger.info(f"Model Arn: {create_model_response['ModelArn']}")


def create_endpoint_config():
    create_endpoint_config_response = sm_client.create_endpoint_config(
        EndpointConfigName=Config.endpoint_config_name,
        ProductionVariants=[
            {
                "InstanceType": "ml.m4.xlarge",
                "InitialInstanceCount": 1,
                "InitialVariantWeight": 1,
                "ModelName": Config.model_name,
                "VariantName": "AllTraffic"
            }
        ]
    )
    logger.info(f"Endpoit config Arn: {create_endpoint_config_response['EndpointConfigArn']}")


def create_endpoint():
    """
    
    """
    create_endpoint_response = sm_client.create_endpoint(
        EndpointName=Config.endpoint_name,
        EndpointConfigName=Config.endpoint_config_name
    )
    logger.info(f"Endpoint Arn: {create_endpoint_response['EndpointArn']}")



def get_endpoint_status():
    response = sm_client.describe_endpoint(
        EndpointName=Config.endpoint_name
    )    
    status = response["EndpointStatus"]

    while status == "Creating":
        time.sleep(30)
        response = sm_client.describe_endpoint(
            EndpointName=Config.endpoint_name
        )
        status = response["EndpointStatus"]
        logger.info(f"Endpoint Status: {status}")

    logger.info(f"Endpoint Status: {status}")
    logger.info(f"Endpoint Arn: {response['EndpointArn']}")


def test_endpoint():
    runtime_client = session.client("sagemaker-runtime")
    response = runtime_client.invoke_endpoint(
        EndpointName=Config.endpoint_name,
        ContentType="text/csv",
        Body=Config.sample_payload
    )
    logger.info(f"Response {response}")
    result = response["Body"].read().decode("utf-8")
    logger.info(f"Response result {result}")


    
if __name__ == "__main__":
    model_url = upload_model_to_s3(model_path=Path(Config.model_tar))
    primary_container = get_primary_container(model_url=model_url)
    create_model(primary_container=primary_container)
    create_endpoint_config()
    create_endpoint()
    get_endpoint_status()
    test_endpoint()