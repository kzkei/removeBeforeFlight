# log config
import logging

def setup_logging():
    logging.basicConfig(
        level=logging.INFO, # debug if tracing
        format='%(levelname)s: %(message)s'
    )

