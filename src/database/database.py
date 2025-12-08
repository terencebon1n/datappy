from sqlalchemy import URL, Engine, create_engine
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import Session, sessionmaker

from ..config import settings


class DatabaseManager:
    db_url: URL

    _engine: Engine
    _session: Session

    _async_engine: AsyncEngine
    _async_session: AsyncSession

    def __init__(self, is_async: bool = False) -> None:
        self.is_async: bool = is_async

        self.db_url = URL.create(
            drivername="postgresql+asyncpg" if is_async else "postgresql+psycopg",
            username=settings.postgres.username,
            password=settings.postgres.password,
            host=settings.postgres.host,
            port=settings.postgres.port,
            database=settings.postgres.database,
        )

    def initialize(self) -> None:
        if self.is_async:
            self._async_engine = create_async_engine(
                url=self.db_url,
                pool_size=settings.postgres.config.pool_size,
                max_overflow=settings.postgres.config.max_overflow,
                pool_recycle=settings.postgres.config.pool_recycle,
                pool_timeout=settings.postgres.config.pool_timeout,
                echo=False,
            )
            self._async_session = async_sessionmaker(
                self._async_engine,
                expire_on_commit=False,
            )()
        else:
            self._engine = create_engine(url=self.db_url)
            self._session = sessionmaker(
                self._engine,
                expire_on_commit=False,
            )()

    @property
    def engine(self) -> Engine:
        return self._engine

    @property
    def async_engine(self) -> AsyncEngine:
        return self._async_engine

    @property
    def session(self) -> Session:
        return self._session

    @property
    def async_session(self) -> AsyncSession:
        return self._async_session

    async def close(self) -> None:
        if self.is_async:
            await self._async_session.close()
            await self._async_engine.dispose()
        else:
            self._session.close()
            self._engine.dispose()
