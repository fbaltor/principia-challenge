import io
import pandas as pd
import boto3
from botocore.exceptions import ClientError


poll_bucket = os.environ['POLL_BUCKET']
poll_key = 'poll.csv'

def updatePopulation(event, context):
    """Updates the cities, states and country population bucket

        population.json = {
            countryName: {
                population: [
                    {
                        year: int,
                        value: int
                    },
                ],
                stateName: {
                    population: [
                        {
                            year: int,
                            value: int
                        },
                    ],
                    cityName: {
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

    s3 = boto3.client('s3')

    s3_response = s3.get_object(Bucket=poll_bucket, Key=poll_key)
    poll_df = pd.read_csv(io.StringIO(str(s3_response['Body'].read(), 'utf-8')))

    