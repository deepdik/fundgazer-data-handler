import os

import uvicorn
from dotenv import load_dotenv
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI
from api.routes.apiRoutes import routers
from config.config import get_config

# provide path to .env file , path is relative to project root
load_dotenv('config/environ/.env')

openapi_url = None
if os.environ['ENV'] == 'DEV':
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

# include routes
app.include_router(routers)

from config.database.mongo import MongoManager
from utils.logger import logger_config

logger = logger_config(__name__)


@app.on_event("startup")
async def startup():
    logger.info("db connection startup")
    await MongoManager().connect_to_database(get_config().DB_URI)


@app.on_event("shutdown")
async def shutdown():
    logger.info("db connection stutdown")
    await MongoManager.close_database_connection()

# if __name__ == "__main__":
#     uvicorn.run("server.app:app", host="0.0.0.0", port=8000, reload=True)
