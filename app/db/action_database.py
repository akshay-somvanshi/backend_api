from dotenv import load_dotenv
from client_init import get_bq_client
from google.cloud import bigquery
import os

# Load the environment variables
load_dotenv()
project_id = os.getenv('GOOGLE_PROJECT_ID')
database_id = os.getenv('DATABASE_ID')

def get_actions(user_id):
    # Load client
    client_bq = get_bq_client()
    query = """
            SELECT
            action_id,
            action_name,
            action_type,
            action_description,
            action_spend,
            action_timeline
            FROM `{project_id}.{database_id}.action`
            WHERE user_id = @user_id
        """
    # Add job config to pass the user_id
    query_config = bigquery.QueryJobConfig(
        query_parameters=[
            bigquery.ScalarQueryParameter("user_id", "STRING", user_id)
        ]
    )

    # Query database
    actions = client_bq.query(query=query, job_config=query_config).result()

    