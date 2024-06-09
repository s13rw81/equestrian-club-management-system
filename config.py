import json
import os
from logging_config import log

# env
ENV = os.environ.get('ENVIRONMENT', False)
log.info(f'running in {ENV} environment.')

# read secrets.json
with open("secrets.json", "r") as f:
    SECRETS = json.load(f)

# CONSTANTS
HOST = SECRETS.get('HOST', '0.0.0.0')
PORT = SECRETS.get('PORT', 8000)
DEBUG = False if ENV == 'PROD' else True
DATABASE_NAME = SECRETS['DATABASE_NAME']
DATABASE_MAX_POOL_SIZE = SECRETS['DATABASE_MAX_POOL_SIZE']
