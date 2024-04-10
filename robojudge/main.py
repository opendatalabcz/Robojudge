import asyncio
from multiprocessing import Process

import redis.asyncio as redis
from fastapi_limiter import FastAPILimiter
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from robojudge.tasks.database_initializer import initialize_dbs
from robojudge.tasks.scraping_scheduler import intialize_scheduled_scraping

from robojudge.utils.settings import settings
import robojudge.routers.rulings

tags_metadata = [
    {
        "name": "rulings",
        "description": "Endpoints for fetching rulings based on semantic search and answering questions with LLM.",
    },
]


app = FastAPI(
    title="Robojudge API",
    license_info={
        "name": "Apache 2.0",
        "url": "https://www.apache.org/licenses/LICENSE-2.0.html",
    },
    openapi_tags=tags_metadata,
    swagger_ui_parameters={"defaultModelsExpandDepth": -1},
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[f"{settings.CLIENT_HOST}:{settings.CLIENT_PORT}"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(robojudge.routers.rulings.router)


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
        Process(target=lambda: asyncio.run(initialize_dbs())).start()
    uvicorn.run(app, host=settings.SERVER_HOST, port=settings.SERVER_PORT)

# TODO: rename cases to rulings
