from google.cloud import bigquery, storage
from dotenv import load_dotenv
import os

# Load the environment variables
load_dotenv()
project_id = os.getenv('GOOGLE_PROJECT_ID')
bucket_id = os.getenv('BUCKET_ID')

def get_bq_client():
    return bigquery.Client(project=project_id)

def get_storage_bucket():
    client = storage.Client(project=project_id)
    return client.get_bucket(bucket_id)
