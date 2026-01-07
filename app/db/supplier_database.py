from .client_init import get_bq_client
from google.cloud import bigquery
from dotenv import load_dotenv
import os

load_dotenv()
project_id = os.getenv('GOOGLE_PROJECT_ID')
database_id = os.getenv('DATABASE_ID')

def fetch_supplier(user_id):
    client = get_bq_client()

    query= f"""
        SELECT 
        supplier_id,
        supplier_name,
        supplier_country,
        supplier_type
        FROM `{project_id}.{database_id}.supplier`
        WHERE user_id = @user_id
    """
    # Add job config to pass the user_id
    query_config = bigquery.QueryJobConfig(
        query_parameters=[
            bigquery.ScalarQueryParameter("user_id", "STRING", user_id)
        ]
    )

    # Query database
    suppliers = client.query(query, job_config=query_config).result()

    out = [dict(row) for row in suppliers]
    return out