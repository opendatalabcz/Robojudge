import asyncio

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from icecream import install

from robojudge.utils.logger import logging
from robojudge.utils.settings import settings

import robojudge.routers.cases
import robojudge.routers.summaries

if settings.ENVIRONMENT == 'dev':
    install()

app = FastAPI()

app.add_middleware(CORSMiddleware, allow_origins=[
    f'{settings.CLIENT_HOST}:{settings.CLIENT_PORT}'], allow_methods=["*"], allow_headers=["*"])

app.include_router(robojudge.routers.cases.router)
app.include_router(robojudge.routers.summaries.router)


@app.get('/health')
async def get_health():
    return {"status": "up", "version": settings.SERVER_VERSION, "environment": settings.ENVIRONMENT}

# For debugging purposes, the app runs through docker otherwise
if __name__ == '__main__':
    uvicorn.run(app, host='0.0.0.0', port=settings.SERVER_PORT)

# TODO: Compare summarization with some non-LLM model (if available for Czech)
# TODO: create runnable scripts of the tasks/ dir (with arguments)
# TODO: update env.example
# TODO: remove embedder and unused tokenizer(s)