import json


def hello(event, context):
    data = json.loads(event['body'])

    print(type(data))
    print(data)

    body = {
        "type": type(data),
        "data": data,
    }

    response = {
        "statusCode": 200,
        "body": json.dumps(body)
    }

    return response
