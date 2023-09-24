import logging
import openai

from robojudge.utils.settings import settings

logging.basicConfig(
    format="%(asctime)s.%(msecs)-03d %(name)s.%(funcName)s:%(lineno)-4s %(levelname)-8s %(message)s",
    level=settings.LOG_LEVEL,
)

logging.getLogger("asyncio").setLevel(logging.WARNING)
openai.util.logger.setLevel(logging.WARNING)
logging.getLogger("rocketry").setLevel(logging.INFO)
