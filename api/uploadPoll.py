import json
import io
import os
import re
import unicodedata
import logging

import pandas as pd
import boto3

from utils import key_exists


poll_bucket = os.environ['POLL_BUCKET']
poll_key = 'poll.csv'

def poll_already_exists(client):
    return key_exists(client, poll_bucket, poll_key)

def format_city_name(unformatted_city_name, pattern=re.compile('[\W_]+')):
    city_name = unicodedata.normalize('NFD', unformatted_city_name)
    city_name = city_name.encode("ascii", "ignore")
    city_name = city_name.decode("utf-8")
    city_name = pattern.sub('', city_name)
    city_name = city_name.lower()

    return city_name

def generate_key_series(poll):
    """
        :param poll: a dataframe of the poll file
        :type poll: pandas dataframe
    """
    def create_key(city, state):
        return city + "_" + state

    def create_key_column(row):
        city = format_city_name(row['city'])
        state = row['state'].lower()

        return create_key(city, state)
    return poll.apply(lambda row: create_key_column(row), axis=1)

def uploadPoll(event, context):
    """Upload a csv file to the S3 bucket
    """
    try:
        data = json.loads(event['body'])["data"]
        headers = data.pop(0)
        df = pd.DataFrame(data, columns=headers).drop_duplicates()
        df.columns = ['id', 'date', 'city', 'state', 'voting_intention']
        df = df[~df['city'].str.contains('#')]
        df = df[~df['state'].str.contains('#')]
        df['key'] = generate_key_series(df)
        df.drop_duplicates(subset='key', inplace=True)

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
