# injest raw
import logging, psycopg2, psycopg2.extras
from datetime import datetime
from utils import connections

# setup logging
logger = logging.getLogger(__name__)

def load_raw_states(states, fetched_at):
    logger.info("exec load")

    if not states or len(states) == 0:
        logger.error(f"states passed as null/empty: {states}")
        return
    
    if not fetched_at or fetched_at is not type(datetime.time):
        logger.error(f"fetched_at must be of datetime.time")
        return

    # connect to raw_flight_states table
    conn, cursor = connections.open()
    
    # wrtie to raw_flight_states
    logger.debug(f"Loading {len(states)} flight vectors : {states}")

    insert_query = """
        INSERT INTO raw_flight_states 
        (icao24, callsign, origin_country, time_position,
        last_contact, longitude, latitude, baro_altitude,
        on_ground, velocity, true_track, vertical_rate,
        sensors, geo_altitude, squawk, spi,
        position_source, category, fetched_at)
        VALUES %s
    """

    # comprhend list of tuples for insertion with identical fetched timestamps
    rows = []
    for state in states:
        rows.append(tuple(state) + (fetched_at,))

    # exec rows load
    psycopg2.extras.execute_values(cursor, insert_query, rows)

    # commit transaction and close
    conn.commit()
    connections.close(conn, cursor)

    logger.info("raw load complete")

