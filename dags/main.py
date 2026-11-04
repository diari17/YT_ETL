from airflow import DAG
import pendulum
from datetime import datetime, timedelta
from airflow.operators.trigger_dagrun import TriggerDagRunOperator

from api.video_stats import (
    get_playlist_id, 
    get_video_ids, 
    extract_video_data, 
    save_to_json,
)

from datawarehouse.dwh import staging_table, core_table
from dataquality.soda import yt_etl_data_quality

# Definir le local timezone
local_tz = pendulum.timezone("Africa/Dakar")

# Default args
default_args = {
    'owner': 'Diari', 
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'email': ["diari@gmail.com"],
    # 'retries': 1,
    # 'retry_delay': timedelta(minutes=5),
    "max_active_runs": 1,
    "dagrun_timeout": timedelta(hours=1),
    "start_date": datetime(2025, 1, 1, tzinfo=local_tz),
    # 'end_date': datetime(2030, 12, 31, tzinfo=local_tz),
}

# Variables
staging_schema = "staging"
core_schema = "core"

# DAG 1 produce_json (Extration des data de Utube API et sauvegarde dans un fichier JSON)
with DAG(
    dag_id='produce_json',
    default_args=default_args,
    description='DAG to produce JSON file with raw data',
    schedule='0 14 * * *',  # Run every day at 14h
    catchup=False,  # Do not perform backfill
) as dag_produce:
    
    # define the tasks
    playlist_id = get_playlist_id()
    video_ids = get_video_ids(playlist_id)
    extract_data = extract_video_data(video_ids)
    save_to_json_task = save_to_json(extract_data)

    trigger_update_db = TriggerDagRunOperator(
        task_id="trigger_update_db",
        trigger_dag_id="update_db"
    )

    # define dependencies
    playlist_id >> video_ids >> extract_data >> save_to_json_task

# DAG 2 update_db (Insertion des data dans les tables de la BDD)
with DAG(
    dag_id='update_db',
    default_args=default_args,
    description='DAG to process JSON file and insert data into both staging and core schemas',
    catchup=False,
    schedule=None,  
      
) as dag_update:
    
    # define the tasks
    update_staging = staging_table()
    update_core = core_table()

    trigger_data_quality = TriggerDagRunOperator(
        task_id="trigger_data_quality",
        trigger_dag_id="data_quality"
    )

    # define dependencies
    update_staging >> update_core >> trigger_data_quality

# DAG 3 data_quality (Vérification de la qualité des données dans les deux couches de la BDD)
with DAG(
    dag_id='data_quality',
    default_args=default_args,
    description='DAG to check the data quality on both layers in the db',
    catchup=False,
    schedule_interval=None,  
) as dag_quality:
    
    # define the tasks
    soda_validate_staging = yt_etl_data_quality(staging_schema)
    soda_validate_core = yt_etl_data_quality(core_schema)

    # define dependencies
    soda_validate_staging >> soda_validate_core 