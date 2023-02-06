import boto3
from loguru import logger
# Create the boto3 client for API Gateway
apigw_client = boto3.client('apigateway')


class LambdaHelper:
    def __init__(self):
        self.lambda_client = boto3.client('lambda')
    
    def get_lambda_arn(self, function_name):
        self.lambda_arn = self.lambda_client.get_function(FunctionName='lambda_func')['Configuration']['FunctionArn']
        return self.lambda_arn

    
    def permission_exists(self, function_name, statement_id):
        try:
            response = self.lambda_client.get_policy(
                FunctionName=function_name
            )
            policy = response['Policy']
            if statement_id in policy:
                return True
        except:
            return False
        return False

    def add_permission_for_apigw(self, apigw_arn):
        response = self.permission_exists('lambda_func', 'apigw-test-3')
        if response is False:
            response = self.lambda_client.add_permission(
                FunctionName='lambda_func',
                StatementId='apigw-test-3',
                Action='lambda:InvokeFunction',
                Principal='apigateway.amazonaws.com',
                SourceArn=apigw_arn
            )
        return response


class APIGateWay:
    def __init__(self):
        self.apigw_client = boto3.client('apigateway')
    
    def api_gateway_exists(self, api_name):    
        try:
            api_list = self.apigw_client.get_rest_apis(limit=500)['items']
            for api in api_list:
                if api['name'] == api_name:                    
                    return api['id']
        except:
            return None
        return None

    def create_rest_api(self, name, description, version):
        response = self.apigw_client.create_rest_api(
            name=name,
            description=description,
            version=version
        )        
        api_id = response['id']
        return api_id

    def get_root_id(self, api_id):
        root_id = self.apigw_client.get_resources(restApiId=api_id)['items'][0]['id']
        return root_id


    def get_apigw_arn(self, api_id):
        # import 167; pdb.set_trace()
        # arn = self.apigw_client.get_rest_api(restApiId=api_id)['arn']
        arn = f'arn:aws:execute-api:ap-southeast-2:456891521041:{api_id}/*/POST/post'
        return arn
    
    def check_if_resource_exists(self, api_id, resource_path):
        resources = self.apigw_client.get_resources(restApiId=api_id)['items']
        for resource in resources:
            if resource['path'] == resource_path:
                return resource['id']
        return None

    def create_resource(self, api_id):
        resource_id =  self.check_if_resource_exists(api_id, '/post')
        if resource_id is None:
            resource_id = self.apigw_client.create_resource(
                restApiId=api_id,
                parentId=self.get_root_id(api_id),
                pathPart='post'
            )['id']
        return resource_id

    def check_if_method_exists(self, api_id, resource_id, method):
        methods = self.apigw_client.get_resource(
            restApiId=api_id,
            resourceId=resource_id
        )['resourceMethods']
        if method in methods:
            return True
        return False

    def create_method(self, api_id, resource_id):
        response = self.check_if_method_exists(api_id, resource_id, 'POST')
        if response is False:
            response = self.apigw_client.put_method(
                restApiId=api_id,
                resourceId=resource_id,
                httpMethod='POST',
                authorizationType='NONE'
            )
        return response

    def create_lambda_api_integration(self, api_id, post_id, lambda_arn):
        response = self.apigw_client.put_integration(
            restApiId=api_id,
            resourceId=post_id,
            httpMethod='POST',
            type='AWS_PROXY',
            integrationHttpMethod='POST',
            uri=f'arn:aws:apigateway:{self.apigw_client.meta.region_name}:lambda:path/2015-03-31/functions/{lambda_arn}/invocations'
        )
        return response

    def create_deployment(self, api_id):
        response = self.apigw_client.create_deployment(
            restApiId=api_id,
            stageName='prod'
        )
        return response

    def test_invoke_method(self, api_id, post_id):
        response = self.apigw_client.test_invoke_method(
            restApiId=api_id,
            resourceId=post_id,
            httpMethod='POST',
            body='{"message": "ping"}'
        )
        return response    





apigw = APIGateWay()
lambda_helper = LambdaHelper()

if __name__ == "__main__":
    api_id = apigw.api_gateway_exists('MyAPI')
    if api_id:
        logger.info(f'API exists with id: {api_id}')
    else:
        api_id = apigw.create_rest_api(
            name='MyAPI',
            description="Demo API",
            version='0.0.1'
        )
        logger.info(f'API created with id: {api_id}')
    
    resource_id = apigw.create_resource(api_id)
    logger.info(f'Resource ID: {resource_id}')

    method = apigw.create_method(api_id, resource_id)
    logger.info(f'Method: {method}')

    lambda_arn = lambda_helper.get_lambda_arn('lambda_func')
    logger.info(f'Lambda ARN: {lambda_arn}')

    integration = apigw.create_lambda_api_integration(api_id, resource_id, lambda_arn)
    # logger.info(f'Integration: {integration}')

    apigw_arn = apigw.get_apigw_arn(api_id)
    logger.info(f'API Gateway ARN: {apigw_arn}')

    response = lambda_helper.add_permission_for_apigw(apigw_arn)
    logger.info(f'Lambda Permission: {response}')

    response = apigw.test_invoke_method(api_id, resource_id)
    logger.info(f'Invoke Method: {response}')

    