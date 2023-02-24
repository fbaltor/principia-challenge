import json
import numpy as np

def hello(event, context):
    statement = f"Random number: {np.random.randint(100)}. Numpy version: {np.__version__}"

    body = {
        "message": statement,
        "input": event
    }

    response = {
        "statusCode": 200,
        "body": json.dumps(body)
    }

    return response
