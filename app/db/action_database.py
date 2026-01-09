from dotenv import load_dotenv
from .client_init import get_bq_client
from google.cloud import bigquery
import os

# Load the environment variables
load_dotenv()
project_id = os.getenv('GOOGLE_PROJECT_ID')
database_id = os.getenv('DATABASE_ID')

# Load client
client_bq = get_bq_client()

# Custom exception
class DatabaseError(Exception):
    pass

def fetch_actions(user_id):
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

        # Get dict output
        out = [dict(row) for row in actions]
        return out
    
    except Exception as e:
        raise DatabaseError(str(e))

def delete_action(user_id, action_id):
    query = f"""
            DELETE 
            FROM `{project_id}.{database_id}.action`
            WHERE user_id = @user_id AND action_id = @action_id
        """
    
    # Add job config for parameters
    query_config = bigquery.QueryJobConfig(
        query_parameters=[
            bigquery.ScalarQueryParameters("user_id", "STRING", user_id),
            bigquery.ScalarQueryParameters("action_id", "STRING", action_id)
        ]
    )

    # Query database
    res = client_bq.query(query=query, job_config=query_config).result()

    # Get dict output
    return {"rows_changed": res.num_dml_affected_rows}
    
def update_action(user_id, action_id, co2_red, spend, rev_unlocked):
    query = f"""
            UPDATE `{project_id}.{database_id}.action`
            SET actual_co2_reduced = @co2_red, actual_spend = @spend, actual_revenue_unlocked = @rev_unlocked
            WHERE action_id = @action_id AND user_id = @user_id
        """

    # Job config for parameters
    query_config = bigquery.QueryJobConfig(
        query_parameters=[
            bigquery.ScalarQueryParameters("user_id", "STRING", user_id),
            bigquery.ScalarQueryParameters("action_id", "STRING", action_id),
            bigquery.ScalarQueryParameters("co2_red", "FLOAT", co2_red),
            bigquery.ScalarQueryParameters("spend", "FLOAT", spend),
            bigquery.ScalarQueryParameters("rev_unlocked", "FLOAT", rev_unlocked)
        ]
    )

    # Query database
    res = client_bq.query(query=query, job_config=query_config).result()

    # Get dict output
    return {"rows_changed": res.num_dml_affected_rows}