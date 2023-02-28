import io
import os
import json

import pandas as pd
import boto3

from utils import key_exists

poll_bucket = os.environ['POLL_BUCKET']
pop_bucket = os.environ['POPULATION_BUCKET']
poll_key = 'poll.csv'
pop_key = 'pop.json'

def build_population_tree(poll):
    """
        population.json = {
            countryName: {
                population: [
                    {
                        year: int,
                        value: int
                    },
                ],
                stateKey: {
                    stateName: string,
                    population: [
                        {
                            year: int,
                            value: int
                        },
                    ],
                    cityKey: {
                        cityName: string,
                        population: [
                            {
                                year: int,
                                value: int
                            },
                        ]
                    }
                }
            }
        }
    """
    pop_tree = {
        'brasil': {
            'population': []
        }
    }
    root = pop_tree['brasil']
    for index, row in poll.iterrows():
        key = row['key']
        (keyed_city, _, keyed_state) = key.partition('_')

        if not keyed_state in root:
            root[keyed_state] = {
                'name': row['state'],
                'population': []
            }

        root[keyed_state][keyed_city] = {
            'name': row['city'],
            'population': []
        }
    
    return pop_tree

def updatePopulation(event, context):
    """Updates the cities, states and country population bucket
    """
    s3 = boto3.client('s3')
    s3_object = s3.get_object(Bucket=poll_bucket, Key=poll_key)
    poll_bytes = s3_object['Body'].read()
    poll_string = str(poll_bytes, 'utf-8')
    poll_stream = io.StringIO(poll_string)
    poll = pd.read_csv(poll_stream)
    
    pop_tree = build_population_tree(poll)

    pop_tree_string = json.dumps(pop_tree, indent=2, default=str, ensure_ascii=False)

    s3.put_object(Body=pop_tree_string, Bucket=pop_bucket, Key=pop_key)

    return {
        "statusCode": 200,
        "body": pop_tree_string
    }
