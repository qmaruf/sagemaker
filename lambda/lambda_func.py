def response(event, context):
    response  = {
        "statusCode": 200,
        "body": "ping from lambda"
    }
    return response
    # if event["message"] == "ping":
    #     response["body"] = "pong"
    # else:
    #     response["body"] = "Unknown message"
    # return response