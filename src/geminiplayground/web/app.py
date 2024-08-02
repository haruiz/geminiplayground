from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .api import api
from .ui import ui
from .db.session_manager import sessionmanager
import logging

logger = logging.getLogger("rich")

from .db.models import *


async def initialize_db():
    await sessionmanager.init()
    logger.info("DB initialized")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Api life span
    :return:
    """

    logger.info("app is starting")
    await initialize_db()
    yield
    logger.info("app is shutting down")


app = FastAPI(lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount the sub-apps
apps = {
    "/api": api,
    "/": ui,
}
for path, sub_app in apps.items():
    app.mount(path, sub_app)
