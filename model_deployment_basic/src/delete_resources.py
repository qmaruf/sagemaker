import boto3
from requests import session
from config import Config

def delete_resources():
    session = boto3.Session(profile_name="dev")
    sm_client = session.client("sagemaker")

    sm_client.delete_model(ModelName=Config.model_name)
    sm_client.delete_endpoint_config(EndpointConfigName=Config.endpoint_config_name)
    sm_client.delete_endpoint(EndpointName=Config.endpoint_name)

if __name__ == "__main__":
    delete_resources()