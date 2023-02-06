import boto3
import sys
sys.path.insert(0, "../")
from smlib import deploy as sm_deploy
from smlib import inference as sm_inference
import json
boto3_session = boto3.Session(profile_name="dev")



deploy = sm_deploy.Deploy(boto3_session, "spacy-nermodel")
container = "456891521041.dkr.ecr.ap-southeast-2.amazonaws.com/sm-pretrained-spacy"
deploy.delete_resouces()
deploy.create_model("456891521041.dkr.ecr.ap-southeast-2.amazonaws.com/sm-pretrained-spacy")
deploy.create_endpoint_config(instance_type="ml.g4dn.xlarge")
deploy.create_endpoint()
deploy.get_endpoint_status()


inference = sm_inference.Inference(boto3_session, "spacy-nermodel")

content_type = "application/json"
request_body = {"input": "This is a test with NER in America with Amazon and Microsoft in Seattle, writing random stuff."}
data = json.loads(json.dumps(request_body))
payload = json.dumps(data)

for i in range(20):
    response = inference.invoke_endpoint(
            content_type="application/json", 
            payload=payload
        )
    result = json.loads(response['Body'].read().decode())['output']
    print (i, result)


