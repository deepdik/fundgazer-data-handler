import os

import uvicorn
from dotenv import load_dotenv
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI
from config.config import get_config

# provide path to .env file , path is relative to project root
settings = get_config()

openapi_url = None
if settings.ENV == 'DEV':
    openapi_url = "/openapi.json"

app = FastAPI(openapi_url=openapi_url)


origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# prometheus metrics: https://prometheus.io/
# app.add_middleware(PrometheusMiddleware)
# app.add_route("/metrics", handle_metrics)

from utils.logger import logger_config
logger = logger_config(__name__)

from config.celery.celery import make_celery

celery = make_celery()
celery.conf.update(
    result_expires=36000,
    enable_utc=True,
    timezone=settings.LOCAL_TIME_ZONE,
)

from config.database.mongo import MongoManager
@app.on_event("startup")
async def startup():
    logger.info("db connection startup")
    await MongoManager().connect_to_database(settings.DB_URI)


@app.on_event("shutdown")
async def shutdown():
    logger.info("db connection stutdown")
    await MongoManager.close_database_connection()

# include routes
from api.routes.apiRoutes import routers
app.include_router(routers)


# if __name__ == "__main__":
#     uvicorn.run("server.app:app", host="0.0.0.0", port=8000, reload=True)
