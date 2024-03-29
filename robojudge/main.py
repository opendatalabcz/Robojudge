from multiprocessing import Process

import redis.asyncio as redis
from fastapi_limiter import FastAPILimiter
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from robojudge.tasks.case_scraping import intialize_scheduled_scraping

from robojudge.utils.settings import settings
import robojudge.routers.cases

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[f"{settings.CLIENT_HOST}:{settings.CLIENT_PORT}"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(robojudge.routers.cases.router)


@app.get("/health")
async def get_health():
    return {
        "status": "up",
        "version": settings.SERVER_VERSION,
        "environment": settings.ENVIRONMENT,
    }


@app.on_event("startup")
async def startup():
    redis_connection = redis.from_url(
        f"redis://{settings.REDIS_URL}", encoding="utf-8", decode_responses=True
    )
    await FastAPILimiter.init(redis_connection)


if __name__ == "__main__":
    if settings.ENABLE_AUTOMATIC_SCRAPING:
        Process(target=intialize_scheduled_scraping).start()
    uvicorn.run(app, host=settings.SERVER_HOST, port=settings.SERVER_PORT)

# TODO: Mongo password
# TODO: rename cases to rulings
