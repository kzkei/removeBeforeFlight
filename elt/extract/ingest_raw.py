# raw fetch
import requests, logging

# setup logging
logger = logging.getLogger(__name__)

def fetch_states():
    logger.info("exec fetch")

    # request opensky states api
    response = requests.get("https://opensky-network.org/api/states/all?extended=1")
    response.raise_for_status()

    # jsonify log and return
    states = response.json()["states"]
    logger.info(f"States fetched: {states}")
    logger.info("fetch complete")
    return states
