from .client_init import get_bq_client
from google.cloud import bigquery
from dotenv import load_dotenv
import os
from pydantic import BaseModel
from ..core.exceptions import DatabaseError

load_dotenv()
project_id = os.getenv('GOOGLE_PROJECT_ID')
database_id = os.getenv('DATABASE_ID')

# Define Pydantic model
class Supplier(BaseModel):
    supplier_id: str
    supplier_name: str
    supplier_country: str
    supplier_type: str

# Connect to client
client = get_bq_client()

def fetch_supplier(user_id) -> list[Supplier]:
    try:
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

        out = [Supplier(**dict(row)) for row in suppliers]
        return out
    
    except Exception as e:
        raise DatabaseError("Failed to fetch supplier from BigQuery", e)