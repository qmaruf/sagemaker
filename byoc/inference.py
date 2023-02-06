import json
content_type = "application/json"
request_body = {"input": "This is a test with NER in America with Amazon and Microsoft in Seattle, writing random stuff."}

#Serialize data for endpoint
data = json.loads(json.dumps(request_body))
payload = json.dumps(data)

#Endpoint invocation
response = runtime_sm_client.invoke_endpoint(
    EndpointName=endpoint_name,
    ContentType=content_type,
    Body=payload)

#Parse results
result = json.loads(response['Body'].read().decode())['output']
result