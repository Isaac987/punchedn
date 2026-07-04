from contextlib import asynccontextmanager

from core.config import AppSettings, get_settings
from core.database import connect_to_mongo, disconnect_from_mongo
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

_settings: AppSettings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    await connect_to_mongo(get_settings())

    yield
    await disconnect_from_mongo()


app = FastAPI(
    title=_settings.app_name,
    description=_settings.app_description,
    version=_settings.app_version,
    docs_url=_settings.app_docs_url,
    redoc_url=_settings.app_redoc_url,
    lifespan=lifespan,
)

# TODO: Define a list of origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
