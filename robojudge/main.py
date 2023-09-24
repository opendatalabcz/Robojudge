import asyncio

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from icecream import install

from robojudge.utils.logger import logging
from robojudge.utils.settings import settings
from robojudge.utils.launch import Server, app as app_rocketry
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


async def main():
    "Run Rocketry and FastAPI"
    server = Server(
        config=uvicorn.Config(app, workers=1, loop="asyncio", port=settings.SERVER_PORT)
    )

    api = asyncio.create_task(server.serve())
    scheduled = asyncio.create_task(app_rocketry.serve())

    await asyncio.wait([scheduled, api])


if __name__ == "__main__":
    asyncio.run(main())

# TODO: Compare summarization with some non-LLM model (if available for Czech)
# TODO: Mongo password
