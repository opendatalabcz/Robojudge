import asyncio
from multiprocessing import Process

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from icecream import install

from robojudge.tasks.case_scraping import run_scheduler
from robojudge.utils.logger import logging
from robojudge.utils.settings import settings

import robojudge.routers.cases

if settings.ENVIRONMENT == "dev":
    install()

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


if __name__ == "__main__":
    if settings.ENABLE_AUTOMATIC_SCRAPING:
        Process(target=run_scheduler).start()
    uvicorn.run(app, host=settings.SERVER_HOST, port=settings.SERVER_PORT)

# TODO: Compare summarization with some non-LLM model (if available for Czech)
# TODO: Mongo password
