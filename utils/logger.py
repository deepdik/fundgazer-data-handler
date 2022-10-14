import logging
import os
from datetime import date

from main import env


error_level = logging.DEBUG if env == 'DEV' else logging.ERROR
logging.getLogger("uvicorn.access").setLevel(error_level)
log_file = os.path.join(os.getcwd() + "/logs/", "logs-" + str(date.today()) + ".log")
logging.basicConfig(filename=log_file, format=' %(levelname)s - %(asctime)s - %(module)s - %(message)s',
                    filemode='a', level=error_level)