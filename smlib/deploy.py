from typing import Dict
from pathlib import Path
import boto3
from loguru import logger
import sagemaker
import time

class Deploy:
    def __init__(self, boto3_session: boto3.Session, model_name: str):        
        self.sm_client = boto3_session.client("sagemaker")
        self.s3_client = boto3_session.client("s3")
        self.region = boto3_session.region_name
        self.role = boto3_session.client("iam").get_role(RoleName="SageMakerExecutionRole")["Role"]["Arn"]
        self.model_name = model_name
        self.endpoint_name = f"{model_name}-endpoint"
        self.endpoint_config_name = f"{model_name}-endpoint-config"

        logger.info(f"Endpoint name: {self.endpoint_name}")
        logger.info(f"Endpoint config name: {self.endpoint_config_name}")

    def upload_model_to_s3(self, local_model_path: str, s3_bucket: str, s3_key: str) -> str:
        """Get the trained model from model_path and upload to s3.

        Args:
            model_path (Path): model location (tar file)
        """
        s3.upload_file(
            local_model_path,
            s3_bucket,
            s3_key
        )
        model_url = f"https://s3-{self.region}.amazonaws.com/{s3_bucket}/{s3_key}"
        logger.info(f"Model uploaded from {model_path} to {model_url}")
        return model_url


    def get_primary_container(self, container_ecr_path: str) -> Dict:
        logger.info(f"Container ecr path {container_ecr_path}")
        primary_container = {
            "Image": container_ecr_path
        }
        return primary_container

    def create_model(self, container_ecr_path: str):
        create_model_response = self.sm_client.create_model(
            ModelName=self.model_name,
            ExecutionRoleArn=self.role,
            PrimaryContainer=self.get_primary_container(container_ecr_path)
        )
        logger.info(f"Model Arn: {create_model_response['ModelArn']}")


    def create_endpoint_config(self, instance_type: str):
        create_endpoint_config_response = self.sm_client.create_endpoint_config(
            EndpointConfigName=self.endpoint_config_name,
            ProductionVariants=[
                {
                    "InstanceType": instance_type,
                    "InitialInstanceCount": 1,
                    "InitialVariantWeight": 1,
                    "ModelName": self.model_name,
                    "VariantName": "AllTraffic",                    
                }
            ]
        )
        logger.info(f"Endpoit config Arn: {create_endpoint_config_response['EndpointConfigArn']}")


    def create_endpoint(self):
        create_endpoint_response = self.sm_client.create_endpoint(
            EndpointName=self.endpoint_name,
            EndpointConfigName=self.endpoint_config_name
        )
        logger.info(f"Endpoint Arn: {create_endpoint_response['EndpointArn']}")

    def get_endpoint_status(self):
        response = self.sm_client.describe_endpoint(
            EndpointName=self.endpoint_name
        )    
        status = response["EndpointStatus"]

        while status == "Creating":
            time.sleep(30)
            response = self.sm_client.describe_endpoint(
                EndpointName=self.endpoint_name
            )
            status = response["EndpointStatus"]
            logger.info(f"Endpoint Status: {status}")

        logger.info(f"Endpoint Status: {status}")
        logger.info(f"Endpoint Arn: {response['EndpointArn']}")

    def delete_resouces(self):
        try:
            self.sm_client.delete_endpoint(EndpointName=self.endpoint_name)
            logger.success(f"Endpoint {self.endpoint_name} deleted")
        except Exception as e:
            logger.error(f"Endpoint {self.endpoint_name} does not exist")
            logger.error(e)
        
        try:
            self.sm_client.delete_endpoint_config(EndpointConfigName=self.endpoint_config_name)
            logger.success(f"Endpoint config {self.endpoint_config_name} deleted")
        except Exception as e:
            logger.error(f"Endpoint config {self.endpoint_config_name} does not exist")
            logger.error(e)
        
        try:
            self.sm_client.delete_model(ModelName=self.model_name)
            logger.success(f"Model {self.model_name} deleted")
        except Exception as e:
            logger.error(f"Model {self.model_name} does not exist")
            logger.error(e)


# def test_endpoint():
#     runtime_client = session.client("sagemaker-runtime")
#     response = runtime_client.invoke_endpoint(
#         EndpointName=Config.endpoint_name,
#         ContentType="text/csv",
#         Body=Config.sample_payload
#     )
#     logger.info(f"Response {response}")
#     result = response["Body"].read().decode("utf-8")
#     logger.info(f"Response result {result}")


    
# if __name__ == "__main__":
#     model_url = upload_model_to_s3(model_path=Path(Config.model_tar))
#     primary_container = get_primary_container(model_url=model_url)
#     create_model(primary_container=primary_container)
#     create_endpoint_config()
#     create_endpoint()
#     get_endpoint_status()
#     test_endpoint()