import logging
import openai

from server.utils.settings import settings

logging.basicConfig(
    format='%(asctime)s - %(levelname)s - %(message)s', level=settings.LOG_LEVEL)

logging.getLogger('asyncio').setLevel(logging.WARNING)
openai.util.logger.setLevel(logging.WARNING)