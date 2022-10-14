import os
import logging
from datetime import date
from functools import lru_cache

import uvicorn
from dotenv import load_dotenv
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI
from api.routes.apiRoutes import routers

# provide path to .env file , path is relative to project root
load_dotenv('config/environ/.env')
env = os.environ['ENV']

openapi_url = None
if env == 'DEV':
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

# exception handler
from utils.exception_handler import validation_exception_handler


# logger import
from utils import logger

# include routes
app.include_router(routers)
