from airflow.sdk import dag, task
from airflow.providers.postgres.hooks.postgres import PostgresHook

import logging, subprocess
from datetime import timedelta, datetime

# set up module logger
logger = logging.getLogger(__name__)

# specify retry behavior and defaults
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 3,
    'retry_delay': timedelta(minutes=5),
    'retry_exponential_backoff': True,
    'max_retry_delay': timedelta(minutes=60),
}

@dag(
    default_args=default_args,
    schedule="*/5 * * * *", # cron for every 5 minutes
)
def live_flights_pipeline():
    """ Ingest, stage and transform with dbt - DAG pipeline def """

    @task
    def ingest():
       
       from elt.extract.ingest_raw import fetch_states

       logger.info("fetching state vectors")
       states = fetch_states()
           
       logger.info(f"{len(states)} states fetched")
       return states

    @task
    def load(states):
        from elt.load.load_raw import load_raw_states

        if not states or len(states) == 0:
            logger.error(f"states is null/empty: {states}")
            return
        
        logger.info(f"attempting load for {len(states)} state vector records")
        
        # open postgres hook where conn is necessary
        hook = PostgresHook(postgres_conn_id="removebeforeflight_app")
        conn = hook.get_conn()
        fetched_at = datetime.now()

        # load raw
        load_raw_states(states, fetched_at, conn)
        conn.close()
        logger.info("raw state vector loading complete")
        return
    
    @task
    def dbt_exec():

        logger.info("dbt run executing")
        
        # exec dbt run -- stage to fct
        result = subprocess.run(
            ["dbt", "run", "--project-dir", "/opt/airflow/rbf", "--profiles-dir", "/opt/airflow/rbf"],
            capture_output=True,
            text=True
            )
        logger.info(result.stdout)

        # raise exception on unsuccessful status code
        if result.returncode != 0:
            logger.error(result.stderr)
            raise Exception("failed on dbt run")
        
        logger.info("dbt run complete")
        return
        
    # define task flow
    states = ingest()
    load(states=states)
    dbt_exec()

# exec dag pipeline
live_flights_pipeline()

