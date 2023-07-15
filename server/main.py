import asyncio

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from server.utils.logger import logging
from server.utils.settings import settings

import server.routers.cases
import server.routers.summaries

app = FastAPI()

# TODO: Env the FE URL
app.add_middleware(CORSMiddleware, allow_origins=[
               'http://localhost:3000'], allow_methods=["*"], allow_headers=["*"])

app.include_router(server.routers.cases.router)
app.include_router(server.routers.summaries.router)

if __name__ == '__main__':
    uvicorn.run(app, port=settings.APP_PORT)
