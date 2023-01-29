def response(event, context):
    response  = {
        "statusCode": 200,
        "body": None
    }
    if event["message"] == "ping":
        response["body"] = "pong"
    else:
        response["body"] = "Unknown message"
    return response