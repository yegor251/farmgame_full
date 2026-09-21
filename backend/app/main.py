import logging
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI, WebSocket

from app.auth.telegram_init_data import TelegramInitDataValidator
from app.config import settings
from app.persistence.db import engine, session_scope
from app.persistence.models import Base
from app.persistence.repository import (
    SqlDepositRepository,
    SqlUserRepository,
    SqlWithdrawRepository,
)
from app.persistence.snapshot_store import SnapshotStore
from app.static_data.catalog import load_catalog
from app.ws.connection_handler import ConnectionHandler

logging.basicConfig(level=logging.INFO if settings.debug else logging.WARNING)

_init_data_validator = TelegramInitDataValidator(
    settings.bot_token, settings.init_data_ttl_seconds, settings.dev_fallback_tg_id
)
_snapshot_store = SnapshotStore(settings.sessions_dir)


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    load_catalog(settings.resources_dir)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield


app = FastAPI(lifespan=lifespan)


@app.websocket("/")
async def websocket_endpoint(websocket: WebSocket) -> None:
    await websocket.accept()
    async with session_scope() as session:
        handler = ConnectionHandler(
            websocket=websocket,
            init_data_validator=_init_data_validator,
            snapshot_store=_snapshot_store,
            user_repository=SqlUserRepository(session),
            deposit_repository=SqlDepositRepository(session),
            withdraw_repository=SqlWithdrawRepository(session),
        )
        await handler.run()