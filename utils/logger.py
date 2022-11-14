import logging
import os
from datetime import date


def logger_config(module):
    """
    LOGGER function. Extends Python loggin module and set a custom config.
    params: Module name to __name__ magic method.
    return: Logger object
    usage: logger_config(__name__)
    """
    level = logging.DEBUG if os.environ['ENV'] == 'DEV' else logging.ERROR
    log_file = os.path.join(os.getcwd() + "/logs/", "logs-" + str(date.today()) + ".log")
    logging.basicConfig(filename=log_file, format=' %(levelname)s - %(asctime)s - %(module)s - %(message)s',
                        filemode='a', level=level)
    handler = logging.StreamHandler()
    logger = logging.getLogger(module)
    logger.setLevel(os.getenv("LOG_LEVEL", level))
    logger.addHandler(handler)
    return logger
