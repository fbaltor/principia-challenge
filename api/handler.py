import json


def hello(event, context):
    data = json.loads(event['body'])

    print(type(data))
    print(data)

    body = {
        "type": type(data).__name__,
        "data": data
    }

    response = {
        "statusCode": 200,
        "body": json.dumps(body)
    }

    return response
