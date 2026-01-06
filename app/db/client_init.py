from google.cloud import bigquery
from dotenv import load_dotenv
import os

# Load the environment variables
load_dotenv()
project_id = os.getenv('GOOGLE_PROJECT_ID')

def get_bq_client():
    return bigquery.Client(project=project_id)