import json
import os
from logging_config import log

# env
ENV = os.environ.get('ENVIRONMENT', False)
log.info(f'running in {ENV} environment.')

# read secrets.json
SECRETS = dict()
try:
    secrets_file = open('secrets.json', 'r')
    SECRETS = json.loads(secrets_file.read())
    secrets_file.close()

except FileNotFoundError:
    log.error('secrets.json not found.')
except Exception as e:
    log.error(e)


# CONSTANTS
HOST = SECRETS.get('HOST', '0.0.0.0')
PORT = SECRETS.get('PORT', 80)
DEBUG = False if ENV == 'PROD' else True
