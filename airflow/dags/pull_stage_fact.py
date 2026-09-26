from airflow.sdk import dag, task
from airflow.providers.postgres.hooks.postgres import PostgresHook

import logging, subprocess
from datetime import timedelta, datetime, timezone

# set up module logger
logger = logging.getLogger(__name__)

# specify retry behavior and args for high frequency cron
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1, # retry once, fail fast, wait for next interval
    'retry_delay': timedelta(seconds=15),
    'retry_exponential_backoff': False,
    'catch_up': False
}

@dag(
    default_args=default_args,
    schedule="*/1 * * * *", # cron for every 1 minute
    max_active_runs=1, # prevent overlapping runs
    catchup=False
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
        fetched_at = datetime.now(timezone.utc)

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
        
    # define task flow - ingest and load steps are separated by xcom
    states = ingest()
    load_task = load(states=states)
    dbt_task = dbt_exec()

    # force wait with task dependency
    load_task >> dbt_task

# exec dag pipeline
live_flights_pipeline()

