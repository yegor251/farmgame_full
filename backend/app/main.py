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

_init_data_validator = TelegramInitDataValidator(
    settings.bot_token, settings.init_data_ttl_seconds, settings.dev_fallback_tg_id
)
_snapshot_store = SnapshotStore(settings.sessions_dir)


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    print("LIFESPAN: start", flush=True)
    load_catalog(settings.resources_dir)
    print("LIFESPAN: catalog loaded", flush=True)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("LIFESPAN: db initialized, ready", flush=True)
    yield
    print("LIFESPAN: shutdown", flush=True)


app = FastAPI(lifespan=lifespan)


@app.websocket("/")
async def websocket_endpoint(websocket: WebSocket) -> None:
    print(f"WS: endpoint called, headers={dict(websocket.headers)}", flush=True)
    try:
        await websocket.accept()
        print("WS: accepted", flush=True)
    except Exception as e:
        print(f"WS: failed to accept: {e!r}", flush=True)
        return

    print("WS: entering session_scope", flush=True)
    try:
        async with session_scope() as session:
            print("WS: session_scope entered", flush=True)

            handler = ConnectionHandler(
                websocket=websocket,
                init_data_validator=_init_data_validator,
                snapshot_store=_snapshot_store,
                user_repository=SqlUserRepository(session),
                deposit_repository=SqlDepositRepository(session),
                withdraw_repository=SqlWithdrawRepository(session),
            )
            print("WS: handler created, calling run()", flush=True)

            await handler.run()

            print("WS: handler.run() finished normally", flush=True)
    except WebSocketDisconnect:
        print("WS: client disconnected", flush=True)
    except Exception as e:
        print(f"WS: unhandled error: {e!r}", flush=True)
        import traceback
        traceback.print_exc()
    finally:
        print("WS: endpoint exiting", flush=True)