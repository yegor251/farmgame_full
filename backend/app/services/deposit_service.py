from typing import TYPE_CHECKING

from app.domain.player import Player
from app.errors import GameErrorCode
from app.persistence.contracts import DepositRepository

if TYPE_CHECKING:
    from app.domain.game import Game


def proceed_to_balance(player: Player, amount: int, jetton_signature: str) -> None:
    if jetton_signature == "TON":
        player.wallet.ton_balance += amount
    elif jetton_signature == "USD":
        player.wallet.usdt_balance += amount
    elif jetton_signature == "TFC":
        player.wallet.token_balance += amount


def claim(game: "Game", deposit_id: int) -> int:
    deposits = game.transfer_info.deposits
    if deposit_id < 0 or deposit_id >= len(deposits):
        return GameErrorCode.GAME_EVENT_OUT_OF_BOUNDARIES

    deposit = deposits[deposit_id]
    if not deposit.active:
        return GameErrorCode.DEPOSIT_ALREADY_ACTIVATED

    deposit.active = False
    proceed_to_balance(game.player, deposit.amount, deposit.jetton_signature)
    return GameErrorCode.OK


async def check(game: "Game", deposit_repository: DepositRepository) -> int:
    error_occured = False
    for deposit in await deposit_repository.get_deposits_by_user_id(game.client_info.tg_id):
        if await deposit_repository.close_deposit_by_transaction_id(deposit.transaction_id):
            game.transfer_info.deposits.append(deposit)
        else:
            error_occured = True
    return GameErrorCode.PAYMENT_ERROR if error_occured else GameErrorCode.OK
