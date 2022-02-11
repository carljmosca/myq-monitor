"""
log utility

"""

import logging
import os

_LOGGER_FORMAT = '%(asctime)s %(message)s'
_LOGGER = logging.getLogger('myq-monitor')

LOGLEVEL = os.environ.get('MYQ_LOGLEVEL', 'INFO').upper()

logging.basicConfig(level=LOGLEVEL, format=_LOGGER_FORMAT)
_LOGGER.info('Log level: %s (change via MYQ_LOGLEVEL env variable)', LOGLEVEL)