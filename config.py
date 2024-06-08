import logging
import os
import sys
from datetime import datetime

WS_LOG_PATH = os.path.join(os.path.curdir, "logs")  # '.\\logs'

if not os.path.exists(WS_LOG_PATH):
    os.makedirs(WS_LOG_PATH)

DATE_FORMAT = "%Y-%m-%d"
TODAY = datetime.now().strftime(DATE_FORMAT)
LOG_FILE = os.path.join(WS_LOG_PATH, f"{TODAY}_logs.log")  # '.\\2023_03_11_10_18_logs.log'

# logging

log = logging.getLogger("khyyal_logger")
log.setLevel(logging.DEBUG)
logFormatter = logging.Formatter('%(asctime)s - %(filename)s > %(funcName)s() # %(lineno)d [%(levelname)s] %(message)s')

consoleHandler = logging.StreamHandler(stream=sys.stderr)
consoleHandler.setFormatter(logFormatter)
log.addHandler(consoleHandler)

fileHandler = logging.FileHandler(LOG_FILE)  # '.\\logs/.\\2023_03_11_10_18_logs.log'
fileHandler.setFormatter(logFormatter)
log.addHandler(fileHandler)

# env
try:
    ENV = os.environ['ENVIRONMENT']
    log.info(f'running in {ENV} environment.')
except KeyError:
    log.error(f'ENV not set')
