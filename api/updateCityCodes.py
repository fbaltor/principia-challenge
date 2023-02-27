import json
import io
import os
import pandas as pd
import requests
import boto3
from botocore.exceptions import ClientError

URL_LOCALIDADES = "https://servicodados.ibge.gov.br/api/v1/localidades/municipios"

def updateCityCodes(event, context):
    """Update the IBGE city location codes city_to_code.json
    """
    r = requests.get(URL_LOCALIDADES)
    r.raise_for_status()

    print(r.content)




