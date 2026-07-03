from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from core.config import get_settings, settings_dependency
from core.database import connect_to_mongo, disconnect_from_mongo


@asynccontextmanager
async def lifespan(app: FastAPI):
    await connect_to_mongo(get_settings())
    yield
    await disconnect_from_mongo()


app = FastAPI(
    title=get_settings().app_name,
    description=get_settings().app_description,
    version=get_settings().app_version,
    docs_url=get_settings().app_docs_url,
    redoc_url=get_settings().app_redoc_url,
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
