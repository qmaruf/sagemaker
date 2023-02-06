import imp
from typing import Dict
import boto3

session = boto3.Session(profile_name="dev")
sm_client = session.client("sagemaker")

def create_model(primary_container: Dict):
    create_model_response = sm_client.create_model(
        ModelName=Config.model_name,
        ExecutionRoleArn=role,
        PrimaryContainer=primary_container
    )
    logger.info(f"Model Arn: {create_model_response['ModelArn']}")