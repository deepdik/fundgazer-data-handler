import os

DATABASE_HOST = os.environ['DATABASE_HOST']
POOL_SIZE = os.environ['POOL_SIZE']
POOL_RECYCLE = os.environ['POOL_RECYCLE']
POOL_TIMEOUT = os.environ['POOL_TIMEOUT']
MAX_OVERFLOW = os.environ['MAX_OVERFLOW']
CONNECT_TIMEOUT = os.environ['CONNECT_TIMEOUT']


class Database():
    def __init__(self) -> None:
        self.connection_is_active = False
        self.engine = None

    def get_db_connection(self):
        pass

    def get_db_session(self, engine):
        pass
