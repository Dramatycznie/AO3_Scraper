import logging


def setup_logging():
    logging.basicConfig(filename='app.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    logger = logging.getLogger(__name__)
    logger.info("Program started.")
    return logger


def log_program_closure(logger):
    logger.info("Program closed.")
