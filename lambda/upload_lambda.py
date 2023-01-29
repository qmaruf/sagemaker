from loguru import logger
import boto3
import zipfile
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('--function_name', type=str, required=True)
parser.add_argument('--handler_name', type=str, required=True)
parser.add_argument('--role', type=str, required=True)
args = parser.parse_args()

function_name = args.function_name
handler_name = args.handler_name
role = args.role

lambda_client = boto3.client('lambda')

def create_zip(function_name):
    with zipfile.ZipFile(f'{function_name}.zip', 'w') as zf:
        zf.write(f'{function_name}.py')

def lambda_function_exist(function_name):
    try:
        lambda_client.get_function(FunctionName=function_name)
        return True
    except lambda_client.exceptions.ResourceNotFoundException:
        return False

def update_lambda(function_name):
    response = lambda_client.update_function_code(
        FunctionName=function_name,
        ZipFile=open(f'{function_name}.zip', 'rb').read()
    )
    
def create_lambda(function_name):
    response = lambda_client.create_function(
        FunctionName=function_name,
        Runtime='python3.8',
        Role=role,
        Handler=f'{function_name}.{handler_name}',
        Code={
            'ZipFile': open(f'{function_name}.zip', 'rb').read()
        }
    )

if __name__ == '__main__':
    create_zip(function_name)
    if lambda_function_exist(function_name):
        logger.info(f'Updating function {function_name}')
        update_lambda(function_name)
    else:
        logger.info(f'Creating function {function_name}')
        create_lambda(function_name)
    
