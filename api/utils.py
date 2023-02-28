from botocore.exceptions import ClientError


def key_exists(client, bucket, file_key):
    """ Check if a given key (file) at a given bucket already exists
    """
    try:
        client.head_object(Bucket=bucket, Key=file_key)
    except ClientError as e:
        if e.response['Error']['Code'] == "404":
            return False
        logging.error(e)
        raise e
    return True