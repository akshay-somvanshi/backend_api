from dotenv import load_dotenv
from .client_init import get_bq_client
from ..core.exceptions import DatabaseError
from google.cloud import bigquery
import os
from pydantic import BaseModel
from datetime import datetime

# Load the environment variables
load_dotenv()
project_id = os.getenv('GOOGLE_PROJECT_ID')
database_id = os.getenv('DATABASE_ID')

# Load client
client_bq = get_bq_client()

# Define Pydantic model
class Action(BaseModel):
    action_id: str
    action_name: str
    action_type: str
    action_description: str
    estimated_spend: float
    estimated_co2_reduced: float
    estimated_revenue_unlocked: float
    plan_id: str 
    timeline_start: datetime
    timeline_end: datetime
    status: str

def fetch_actions(user_id) -> list[Action]:
    try:
        query = f"""
                SELECT
                action_id,
                action_name,
                action_type,
                action_description,
                estimated_spend,
                estimated_co2_reduced,
                estimated_revenue_unlocked,
                plan_id,
                timeline_start,
                timeline_end, 
                status
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

        # Get the list of Actions
        out = [Action(**dict(row)) for row in actions] # ** is the unpacking operator - unpacks dict into keyword argument
        return out
    
    except Exception as e:
        raise DatabaseError("Failed to fetch actions", e)

def delete_action(user_id, action_id):
    try:
        query = f"""
                DELETE 
                FROM `{project_id}.{database_id}.action`
                WHERE user_id = @user_id AND action_id = @action_id
            """
        
        # Add job config for parameters
        query_config = bigquery.QueryJobConfig(
            query_parameters=[
                bigquery.ScalarQueryParameter("user_id", "STRING", user_id),
                bigquery.ScalarQueryParameter("action_id", "STRING", action_id)
            ]
        )

        # Query database
        res = client_bq.query(query=query, job_config=query_config).result()

        # Get dict output
        return {"rows_changed": res.num_dml_affected_rows}
    
    except Exception as e:
        raise DatabaseError("Failed to delete action", e)
    
def update_action_service(user_id, action_id, co2_red, spend, rev_unlocked):
    try:
        query = f"""
                UPDATE `{project_id}.{database_id}.action`
                SET actual_co2_reduced = @co2_red, actual_spend = @spend, actual_revenue_unlocked = @rev_unlocked
                WHERE action_id = @action_id AND user_id = @user_id
            """

        # Job config for parameters
        query_config = bigquery.QueryJobConfig(
            query_parameters=[
                bigquery.ScalarQueryParameter("user_id", "STRING", user_id),
                bigquery.ScalarQueryParameter("action_id", "STRING", action_id),
                bigquery.ScalarQueryParameter("co2_red", "FLOAT", co2_red),
                bigquery.ScalarQueryParameter("spend", "FLOAT", spend),
                bigquery.ScalarQueryParameter("rev_unlocked", "FLOAT", rev_unlocked)
            ]
        )

        # Query database
        res = client_bq.query(query=query, job_config=query_config).result()

        # Get dict output
        return {"rows_changed": res.num_dml_affected_rows}
    
    except Exception as e:
        raise DatabaseError("Failed to update action", e)