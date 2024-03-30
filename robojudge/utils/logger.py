import logging

from robojudge.utils.settings import settings

# Remove too verbose logs
logging.getLogger("asyncio").setLevel(logging.WARNING)
logging.getLogger("rocketry").setLevel(logging.INFO)
logging.getLogger("httpcore").setLevel(logging.INFO)
logging.getLogger("httpx").setLevel(logging.ERROR)

logging.basicConfig(
    format="%(asctime)s.%(msecs)-03d %(name)s.%(funcName)s:%(lineno)-4s %(levelname)-8s %(message)s",
    level=settings.LOG_LEVEL,
)
