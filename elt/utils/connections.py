# connection operation util
import psycopg2
from dotenv import load_dotenv, find_dotenv
import os, logging

# setup logging
logger = logging.getLogger(__name__)

# load .env vars with find
load_dotenv(find_dotenv())

# load db config
DB_CONFIG = {
    'host': os.getenv('DB_HOST'),
    'port': int(os.getenv('DB_PORT', 5435)),
    'user': os.getenv('DB_USER', 'removebeforeflight'),
    'password': os.getenv('DB_PASSWORD'),
    'database': os.getenv('DB_NAME', 'removebeforeflight')
}

# validate DB_CONFIG password
if not DB_CONFIG['password']:
    raise ValueError("DB_PASSWORD env var required")

# opens db conn
# returns configured open conn, cursor
def open():
    logger.info("opening db connection")
    conn = psycopg2.connect(**DB_CONFIG)
    cursor = conn.cursor()

    logger.info("db connected")
    return conn, cursor

# closes db connection with given open conn, cursor params
def close(conn, cursor):
    logger.info("closing connection")

    try:
        cursor.close()
        conn.close()

        logger.info("connection closed")
        return
    
    except Exception as e:
        logger.error(f"failed to close connection: {e}")
        raise
        