from contextlib import asynccontextmanager

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    async_sessionmaker,
    create_async_engine,
)

from core.config import db_settings

DATABASE_URL = db_settings.db_url
ECHO = db_settings.db_echo


class DataBaseHelper:
    def __init__(self, db_url: str, echo: bool):
        self.__engine: AsyncEngine = create_async_engine(db_url, echo=echo)
        self.__session_factory = async_sessionmaker(
            bind=self.__engine,
            expire_on_commit=False,
            autoflush=False,
            autocommit=False,
        )

    @asynccontextmanager
    async def session_dependency(self):
        async with self.__session_factory() as session:
            yield session
            await session.close()


db_helper = DataBaseHelper(DATABASE_URL, ECHO)
