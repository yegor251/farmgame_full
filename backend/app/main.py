import logging
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI, WebSocket
from starlette.websockets import WebSocketDisconnect

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
logger = logging.getLogger(__name__)

_init_data_validator = TelegramInitDataValidator(
    settings.bot_token, settings.init_data_ttl_seconds, settings.dev_fallback_tg_id
)
_snapshot_store = SnapshotStore(settings.sessions_dir)


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    logger.info("LIFESPAN: start")
    load_catalog(settings.resources_dir)
    logger.info("LIFESPAN: catalog loaded")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("LIFESPAN: db initialized, ready")
    yield
    logger.info("LIFESPAN: shutdown")


app = FastAPI(lifespan=lifespan)


@app.websocket("/")
async def websocket_endpoint(websocket: WebSocket) -> None:
    logger.info("WS: endpoint called, headers=%s", dict(websocket.headers))
    try:
        await websocket.accept()
        logger.info("WS: accepted")
    except Exception:
        logger.exception("WS: failed to accept")
        return

    logger.info("WS: entering session_scope")
    try:
        async with session_scope() as session:
            logger.info("WS: session_scope entered")

            handler = ConnectionHandler(
                websocket=websocket,
                init_data_validator=_init_data_validator,
                snapshot_store=_snapshot_store,
                user_repository=SqlUserRepository(session),
                deposit_repository=SqlDepositRepository(session),
                withdraw_repository=SqlWithdrawRepository(session),
            )
            logger.info("WS: handler created, calling run()")

            await handler.run()

            logger.info("WS: handler.run() finished normally")
    except WebSocketDisconnect:
        logger.info("WS: client disconnected")
    except Exception:
        logger.exception("WS: unhandled error")
    finally:
        logger.info("WS: endpoint exiting")