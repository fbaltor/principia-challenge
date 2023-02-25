import json
import io
import pandas as pd
import logging
import boto3

from botocore.exceptions import ClientError
import os

bucket_name = os.environ['S3_BUCKET_NAME']
poll_file_name = 'poll.csv'


def upload_file(file_name, bucket, object_name=None):
    """Upload a file to an S3 bucket

    :param file_name: File to upload
    :param bucket: Bucket to upload to
    :param object_name: S3 object name. If not specified then file_name is used
    :return: True if file was uploaded, else False
    """

    # If S3 object_name was not specified, use file_name
    if object_name is None:
        object_name = os.path.basename(file_name)

    # Upload the file
    s3_client = boto3.client('s3')
    try:
        response = s3_client.upload_file(file_name, bucket, object_name)
    except ClientError as e:
        logging.error(e)
        return False
    return True

def clean_poll_file(poll_file):
    df = pd.read_csv(poll_file, encoding="latin_1", sep=";")
    df.columns = ['id', 'date', 'city_name', 'city_state', 'voting_intentions']
    return df.to_csv(sep=";", encoding="utf-8", index=False)

def poll_already_exists(client):
    try:
        client.head_object(Bucket=bucket_name, Key=poll_file_name)
    except botocore.exceptions.ClientError as e:
        if e.response['Error']['Code'] == "404":
            return False
        
        logging.error(e)
        raise e
    
    return True


def upload_poll(event, context):
    """Upload a csv file to the S3 bucket
    """
    try:
        data = json.loads(event['body'])
        new_poll = clean_poll_file(data)
    except pd.errors.ParseError as e:
        logging.error(e)
        return {
            "statusCode": 422,
            "body": "Invalid poll format"
        }
    
    s3_client = boto3.client('s3')

    if not poll_already_exists(s3_client):
        s3_client.put_object(
            Body=new_poll,
            Bucket=bucket_name,
            Key=poll_file_name
        )