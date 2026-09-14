import logging

from fastapi import WebSocket, WebSocketDisconnect

from app.api_models.builders import build_state_response
from app.auth.telegram_init_data import TelegramInitDataValidator
from app.config import settings
from app.domain.game import Game
from app.errors import GameErrorCode
from app.persistence.contracts import DepositRepository, UserRepository, WithdrawRepository
from app.persistence.snapshot_store import SnapshotStore
from app.services.building_service import building_exists
from app.ws import protocol
from app.ws.protocol import Command

logger = logging.getLogger(__name__)

_STRIKE_CODES = (GameErrorCode.SOCKET_WRONG_FORMAT, GameErrorCode.SOCKET_UNKNOWN)


class ConnectionHandler:
    def __init__(
        self,
        websocket: WebSocket,
        init_data_validator: TelegramInitDataValidator,
        snapshot_store: SnapshotStore,
        user_repository: UserRepository,
        deposit_repository: DepositRepository,
        withdraw_repository: WithdrawRepository,
    ) -> None:
        self._websocket = websocket
        self._init_data_validator = init_data_validator
        self._snapshot_store = snapshot_store
        self._user_repository = user_repository
        self._deposit_repository = deposit_repository
        self._withdraw_repository = withdraw_repository
        self._game: Game | None = None

    async def run(self) -> None:
        try:
            while True:
                message = await self._websocket.receive_text()
                should_continue = await self._handle_message(message)
                if not should_continue:
                    return
        except WebSocketDisconnect:
            pass
        finally:
            if self._game is not None:
                self._snapshot_store.save_game(self._game)

    async def _handle_message(self, message: str) -> bool:
        command = protocol.parse_command(message, self._init_data_validator)

        if isinstance(command, protocol.Connect):
            game = await self._handle_connect(command)
            if game is None:
                return False
            self._game = game
        else:
            if self._game is None:
                return True
            await self._dispatch(self._game, command)
            if self._game.last_operation in _STRIKE_CODES:
                self._game.client_info.strikes += 1
            if settings.debug:
                logger.info("%s - %s - %s", self._game.client_info.tg_id, message, self._game.last_operation)
            if self._game.client_info.banned:
                self._snapshot_store.save_game(self._game)
                await self._websocket.close()
                return False

        response = build_state_response(self._game)
        await self._websocket.send_text(response.model_dump_json(by_alias=True, exclude_none=True))
        return True

    async def _handle_connect(self, command: protocol.Connect) -> Game | None:
        auth = command.auth
        if auth is None:
            return None

        tg_id = auth.tg_id
        user = await self._user_repository.player_by_id(tg_id)
        if user is None:
            if not auth.is_verified:
                return None
            if not await self._user_repository.create_user(tg_id, auth.ref_id):
                return None
            user = await self._user_repository.player_by_id(tg_id)
            if user is None:
                return None

        if not user.active:
            game = Game(user.user_id, user.ref_id)
            game.first_init()
            self._snapshot_store.save_game(game)
            await game.on_connect(self._deposit_repository, self._withdraw_repository)
            await self._user_repository.activate_user_by_id(user.user_id)

            if user.ref_id > 0 and user.ref_id != user.user_id:
                await self._add_referral(user.user_id, user.ref_id)
        else:
            game = self._snapshot_store.load_game(tg_id)
            if game.client_info.banned:
                await self._websocket.close()
                return None
            await game.on_connect(self._deposit_repository, self._withdraw_repository)

        return game

    async def _add_referral(self, referred_id: int, referrer_id: int) -> None:
        if not self._snapshot_store.exists(referrer_id):
            return
        referrer_game = self._snapshot_store.load_game(referrer_id)
        referrer_game.client_info.referrals.append(referred_id)
        referrer_game.player.wallet.token_balance += 1000
        self._snapshot_store.save_game(referrer_game)

    async def _dispatch(self, game: Game, command: Command) -> None:
        if isinstance(command, protocol.Use):
            game.on_use(command.name, command.x, command.y)
        elif isinstance(command, protocol.Collect):
            game.on_collect(command.x, command.y)
        elif isinstance(command, protocol.Upgrade):
            game.on_upgrade(command.x, command.y)
        elif isinstance(command, protocol.Buy):
            if command.amount > 0:
                game.on_buy(command.name, command.amount)
            else:
                game.last_operation = GameErrorCode.SOCKET_WRONG_FORMAT
        elif isinstance(command, protocol.Place):
            if building_exists(command.name):
                game.on_place(command.name, command.x, command.y)
            else:
                game.last_operation = GameErrorCode.SOCKET_WRONG_FORMAT
        elif isinstance(command, protocol.Move):
            game.on_move(command.x, command.y, command.to_x, command.to_y)
        elif isinstance(command, protocol.SpinWheel):
            game.on_spin()
        elif isinstance(command, protocol.Regeneration):
            game.on_regenerate()
        elif isinstance(command, protocol.OrderOperation):
            if command.operation == "complete":
                game.on_complete_order(command.index)
            elif command.operation == "reroll":
                game.on_reroll_order(command.index)
            else:
                game.last_operation = GameErrorCode.SOCKET_WRONG_FORMAT
        elif isinstance(command, protocol.ClaimDeposit):
            game.on_claim_deposit(command.index)
        elif isinstance(command, protocol.RegisterWithdraw):
            await game.on_register_withdraw(command.amount, command.wallet, self._withdraw_repository)
        elif isinstance(command, protocol.PurchaseSlot):
            game.on_purchase_slot(command.x, command.y)
        elif isinstance(command, protocol.PurchaseDeal):
            game.on_purchase_deal(command.name)
        elif isinstance(command, protocol.ActivateBooster):
            game.on_activate_booster(command.index)
        elif isinstance(command, protocol.InvUpgrade):
            game.on_inventory_upgrade()
        elif isinstance(command, protocol.RemoveObstacle):
            game.on_remove_obstacle(command.x, command.y)
        else:
            game.last_operation = GameErrorCode.SOCKET_WRONG_FORMAT
