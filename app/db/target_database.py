from .client_init import get_bq_client
from google.cloud import bigquery
from dotenv import load_dotenv
import os

load_dotenv()
project_id = os.getenv('GOOGLE_PROJECT_ID')
database_id = os.getenv('DATABASE_ID')

# Connect to client
client = get_bq_client()

def fetch_target(user_id):
    query= f"""
        SELECT 
        source,
        target_id,
        target_name,
        target_type,
        target_description,
        unit
        FROM `{project_id}.{database_id}.targets`
        WHERE user_id = @user_id
    """
    # Add job config to pass the user_id
    query_config = bigquery.QueryJobConfig(
        query_parameters=[
            bigquery.ScalarQueryParameter("user_id", "STRING", user_id)
        ]
    )

    # Query database
    targets = client.query(query, job_config=query_config).result()

    out = [dict(row) for row in targets]
    return out