from unittest.mock import AsyncMock, MagicMock, patch

import backend.infrastructure.database.postgres.manager as manager_module
from backend.infrastructure.database.postgres.manager import PostgresDatabaseManager


def test_sync_manager_lifecycle():
    engine = MagicMock()
    engine.execution_options.return_value = engine
    session = MagicMock()
    session_factory = MagicMock(return_value=session)

    with (
        patch.object(manager_module, "create_engine", return_value=engine) as ce,
        patch.object(manager_module, "sessionmaker", return_value=session_factory),
    ):
        manager = PostgresDatabaseManager(is_async=False)
        assert manager.db_url.drivername == "postgresql+psycopg"

        manager.initialize()
        ce.assert_called_once()
        assert manager.engine is engine
        assert manager.session is session

        manager.set_schema("montpellier")
        engine.execution_options.assert_called_once_with(
            schema_translate_map={"gtfs": "montpellier"}
        )

    import asyncio

    asyncio.run(manager.close())
    session.close.assert_called_once()
    engine.dispose.assert_called_once()


async def test_async_manager_lifecycle():
    async_engine = MagicMock()
    async_engine.dispose = AsyncMock()
    async_engine.execution_options.return_value = async_engine

    with patch.object(
        manager_module, "create_async_engine", return_value=async_engine
    ) as cae:
        manager = PostgresDatabaseManager(is_async=True)
        assert manager.db_url.drivername == "postgresql+asyncpg"

        manager.initialize()
        cae.assert_called_once()
        assert manager.async_engine is async_engine

        manager.set_schema("nimes")
        async_engine.execution_options.assert_called_once_with(
            schema_translate_map={"gtfs": "nimes"}
        )

        await manager.close()
        async_engine.dispose.assert_awaited_once()
