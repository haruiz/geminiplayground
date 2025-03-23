import logging
import os
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from .api import api
from .db.models import *  # noqa: F401, F403
from .db.session_manager import sessionmanager
from .web import web

logger = logging.getLogger("rich")


def mount_apps(app: FastAPI):
    apps = {
        "/api": api,
        "/": web,
    }
    for path, sub_app in apps.items():
        app.mount(path, sub_app)


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
    mount_apps(app)
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
