import os

from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase

from config.config import get_config
from utils.logger import logger_config

logger = logger_config(__name__)

setting = get_config()


class MongoManager:
    """
    This class extends from ./database_manager.py
    which have the abstract methods to be re-used here.
    """

    __client: AsyncIOMotorClient = None
    __db: AsyncIOMotorDatabase = None

    @classmethod
    async def get_instance(cls):
        if cls.__db is None:
            cls.__db = await cls.connect_to_database(setting.DB_URI)
        return cls.__db

    # database connect and close connections
    @classmethod
    async def connect_to_database(cls, path: str):
        # logger.info("Connecting to MongoDB")
        print(path, "path")
        cls.__client = AsyncIOMotorClient(
            path,
            # in milliseconds
            maxIdleTimeMS=10000,
            # minimal pool size
            minPoolSize=10,
            # maximal pool size
            maxPoolSize=50,
            # connection timeout in miliseconds
            connectTimeoutMS=10000,
            # boolean
            retryWrites=True,
            # wait queue in miliseconds
            waitQueueTimeoutMS=10000,
            # in miliseconds
            serverSelectionTimeoutMS=10000
        )

        if os.getenv("ENVIRONMENT") == "PRD":
            cls.__db = cls.__client.proddb
        elif os.getenv("ENVIRONMENT") == "STG":
            cls.__db = cls.__client.stagedb
        else:
            cls.__db = cls.__client.devdb

        logger.info(
            "Connected to MongoDB -  %s environment!", os.getenv("ENV")
        )

    @classmethod
    async def close_database_connection(cls):
        logger.info("Closing connection to MongoDB")
        cls.__client.close()
        logger.info("MongoDB connection closed")
