import json
import os
import logging

import pandas as pd
import requests
import boto3
from utils import key_exists, format_city_name, create_key


URL_LOCALIDADES = "https://servicodados.ibge.gov.br/api/v1/localidades/municipios"
pop_bucket = os.environ['POPULATION_BUCKET']
city_key = 'city.json'
city_to_id_key = 'city_to_id.json'

def city_file_already_exists(client):
    return key_exists(client, pop_bucket, city_key)

def get_city_json(client):
    """Get the IBGE JSON list of cities and their id's
    """
    if city_file_already_exists(client):
        s3_object = client.get_object(Bucket=pop_bucket, Key=city_key)
        city_json = json.loads(s3_object['Body'].read().decode('utf8'))
        return city_json
    
    r = requests.get(URL_LOCALIDADES)
    r.raise_for_status()

    city_bytes = r.content

    client.put_object(Body=city_bytes, Bucket=pop_bucket, Key=city_key)

    return json.loads(city_bytes)

def updateCityId(event, context):
    """Update the IBGE city location id's city_to_id.json
    """
    s3 = boto3.client('s3')
    city_json_list = get_city_json(s3)

    city_to_id = dict()
    for city in city_json_list:
        city_name = format_city_name(city['nome'])
        state_name = city['microrregiao']['mesorregiao']['UF']['sigla'].lower()

        key = create_key(city_name, state_name)
        city_to_id[key] = city['id']

    city_to_id_string = json.dumps(city_to_id, indent=2, default=str)

    s3.put_object(Body=city_to_id_string, Bucket=pop_bucket, Key=city_to_id_key)
