import json
import io
import pandas as pd
import logging
import boto3
from botocore.exceptions import ClientError
import os

bucket_name = os.environ['S3_BUCKET_NAME']
poll_key = 'poll.csv'

def poll_already_exists(client):
    try:
        client.head_object(Bucket=bucket_name, Key=poll_key)
    except ClientError as e:
        if e.response['Error']['Code'] == "404":
            return False
        
        logging.error(e)
        raise e
    
    return True


def uploadPoll(event, context):
    """Upload a csv file to the S3 bucket
    """
    try:
        data = json.loads(event['body'])["data"] # list of list
        headers = data.pop(0)
        df = pd.DataFrame(data, columns=headers)
        df.columns = ['id', 'date', 'city_name', 'city_state', 'voting_intentions']

    except pd.errors.ParseError as e:
        logging.error(e)
        return {
            "statusCode": 422,
            "body": "Invalid poll format"
        }
    
    s3_client = boto3.client('s3')

    if not poll_already_exists(s3_client):
        csv_buffer = io.StringIO()
        df.to_csv(csv_buffer)

        s3_client.put_object(
            Body=csv_buffer.getvalue(),
            Bucket=bucket_name,
            Key=poll_key
        )

        return {
            "statusCode": 200
        }