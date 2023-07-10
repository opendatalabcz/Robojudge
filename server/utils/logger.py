import logging

from server.utils.settings import settings

logging.basicConfig(
    format='%(asctime)s - %(levelname)s - %(message)s', level=settings.LOG_LEVEL)
