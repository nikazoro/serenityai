from fastapi import FastAPI
from contextlib import asynccontextmanager

from ..api.routes import router
from ..db.init_db import init_db

@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield

app = FastAPI(title="DreamWeaver AI", lifespan=lifespan)

app.include_router(router)