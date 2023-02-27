import json
import io
import os
import pandas as pd
import logging
import boto3
from botocore.exceptions import ClientError


poll_bucket = os.environ['POLL_BUCKET']
poll_key = 'poll.csv'

def poll_already_exists(client):
    try:
        client.head_object(Bucket=poll_bucket, Key=poll_key)
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
        data = json.loads(event['body'])["data"]
        headers = data.pop(0)
        df = pd.DataFrame(data, columns=headers).drop_duplicates()
        df.columns = ['id', 'date', 'city_name', 'city_state', 'voting_intentions']

    except (pd.errors.ParserError, ValueError) as e:
        logging.error(e)
        return {
            "statusCode": 422,
            "body": "Invalid poll format"
        }
    
    s3_client = boto3.client('s3')

    if poll_already_exists(s3_client):
        s3_response_object = s3_client.get_object(Bucket=poll_bucket, Key=poll_key)
        old_bytes_stream = s3_response_object['Body'].read()
        old_string = str(old_bytes_stream, 'utf-8')
        old_string_stream = io.StringIO(old_string)
        old_df = pd.read_csv(old_string_stream)

        dfs = [old_df, df]
        df = pd.concat(dfs, axis=0, ignore_index=True).drop_duplicates()
    
    csv_buffer = io.StringIO()
    df.to_csv(csv_buffer, index=False)

    s3_client.put_object(
        Body=csv_buffer.getvalue(),
        Bucket=poll_bucket,
        Key=poll_key
    )

    return {
        "statusCode": 200
    }
