import random
from datetime import UTC, datetime
from typing import TYPE_CHECKING

from app.config import settings
from app.domain.transfer_info import Withdraw
from app.errors import GameErrorCode
from app.persistence.contracts import WithdrawRepository

if TYPE_CHECKING:
    from app.domain.game import Game


async def create_withdraw(
    game: "Game", amount: int, wallet: str, withdraw_repository: WithdrawRepository
) -> int:
    if amount > game.player.wallet.token_balance:
        return GameErrorCode.NOT_ENOUGH_MONEY

    if game.player.wallet.ton_balance < settings.withdraw_ton_fee:
        return GameErrorCode.NOT_ENOUGH_MONEY

    withdraw = Withdraw(
        transaction_id=random.randint(0, 1_000_000_000_000_000_000),
        status=0,
        tg_id=game.client_info.tg_id,
        wallet=wallet,
        amount=amount,
        time_stamp=int(datetime.now(UTC).timestamp()),
    )
    if not await withdraw_repository.register_withdraw(withdraw):
        return GameErrorCode.PAYMENT_ERROR

    game.player.wallet.token_balance -= amount
    game.player.wallet.ton_balance -= settings.withdraw_ton_fee
    game.transfer_info.withdraws.append(withdraw)
    return GameErrorCode.OK


async def get_current_status(transaction_id: int, withdraw_repository: WithdrawRepository) -> int:
    withdraw = await withdraw_repository.check_withdraw_by_info(transaction_id)
    return withdraw.status if withdraw is not None else 0


async def check_all_withdraws(game: "Game", withdraw_repository: WithdrawRepository) -> int:
    for withdraw in game.transfer_info.withdraws:
        withdraw.status = await get_current_status(withdraw.transaction_id, withdraw_repository)
    return GameErrorCode.OK
