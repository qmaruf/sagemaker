import boto3
import json

client = boto3.client("apigateway")

def invoke_lambda_via_api(api_id, resource_path, stage_name, function_name, payload):
    # Get the API endpoint URL
    endpoint = f"https://{api_id}.execute-api.{client.meta.region_name}.amazonaws.com/{stage_name}/{resource_path}"

    # Invoke the Lambda function using the endpoint
    response = client.invoke(
        FunctionName=function_name,
        InvocationType="RequestResponse",
        LogType="Tail",
        Payload=json.dumps(payload),
        Endpoint=endpoint
    )

    # Return the response from the Lambda function
    return response["Payload"].read()
