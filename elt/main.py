# main for raw el
from extract.injest_raw import fetch_states
from load.load_raw import load_raw_states
from utils.log_config import setup_logging
from datetime import datetime
import logging


setup_logging()
logger = logging.getLogger(__name__)


def main():
    logger.info("exec main")

    fetched_at = datetime.now()

    # fetch raw states (list of lists)
    states = fetch_states()

    logger.debug(f"States json from fetch: {states}")

    # insert into raw table
    load_raw_states(states, fetched_at)

    # end -> dbt from here
    logger.info("main complete")

if __name__ == "__main__":
    main()