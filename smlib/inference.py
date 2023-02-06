from typing import Dict
from pathlib import Path
import boto3
from loguru import logger
import sagemaker
import time

class Inference:
    def __init__(self, boto3_session: boto3.Session, model_name: str):        
        self.runtime_sm_client = boto3_session.client("sagemaker-runtime")
        self.endpoint_name = f"{model_name}-endpoint"
        self.endpoint_config_name = f"{model_name}-endpoint-config"

        logger.info(f"Model name: {model_name}")
        logger.info(f"Endpoint name: {self.endpoint_name}")
        logger.info(f"Endpoint config name: {self.endpoint_config_name}")

    def invoke_endpoint(self, content_type: str, payload):
        response = self.runtime_sm_client.invoke_endpoint(
            EndpointName=self.endpoint_name,
            ContentType=content_type,
            Body=payload
        )
        return response


    