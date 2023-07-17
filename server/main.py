import asyncio

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from server.utils.logger import logging
from server.utils.settings import settings

import server.routers.cases
import server.routers.summaries

app = FastAPI()

app.add_middleware(CORSMiddleware, allow_origins=[
    f'{settings.CLIENT_HOST}:{settings.CLIENT_PORT}'], allow_methods=["*"], allow_headers=["*"])

app.include_router(server.routers.cases.router)
app.include_router(server.routers.summaries.router)


@app.get('/health')
async def get_health():
    return {"status": "up", "version": settings.SERVER_VERSION, "environment": settings.ENVIRONMENT}

if __name__ == '__main__':
    uvicorn.run(app, host='0.0.0.0', port=settings.SERVER_PORT)
