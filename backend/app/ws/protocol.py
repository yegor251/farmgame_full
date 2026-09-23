from dataclasses import dataclass

from app.auth.telegram_init_data import TelegramAuthResult, TelegramInitDataValidator


@dataclass
class Connect:
    auth: TelegramAuthResult | None


@dataclass
class Use:
    name: str
    x: int
    y: int


@dataclass
class Collect:
    x: int
    y: int


@dataclass
class Upgrade:
    x: int
    y: int


@dataclass
class Buy:
    name: str
    amount: int


@dataclass
class Place:
    name: str
    x: int
    y: int


@dataclass
class Move:
    x: int
    y: int
    to_x: int
    to_y: int


@dataclass
class SpinWheel:
    pass


@dataclass
class OrderOperation:
    operation: str
    index: int


@dataclass
class Regeneration:
    pass


@dataclass
class ClaimDeposit:
    index: int


@dataclass
class PurchaseSlot:
    x: int
    y: int


@dataclass
class PurchaseDeal:
    name: str


@dataclass
class ActivateBooster:
    index: int


@dataclass
class InvUpgrade:
    pass


@dataclass
class RemoveObstacle:
    x: int
    y: int


@dataclass
class Unknown:
    pass


Command = (
    Connect
    | Use
    | Collect
    | Upgrade
    | Buy
    | Place
    | Move
    | SpinWheel
    | OrderOperation
    | Regeneration
    | ClaimDeposit
    | PurchaseSlot
    | PurchaseDeal
    | ActivateBooster
    | InvUpgrade
    | RemoveObstacle
    | Unknown
)


def _split(message: str, parts_count: int) -> list[str] | None:
    parts = message.split("/", parts_count - 1)
    if len(parts) != parts_count:
        return None
    return parts


def parse_command(message: str, init_data_validator: TelegramInitDataValidator) -> Command:
    if message == "spin":
        return SpinWheel()
    if message == "regen":
        return Regeneration()
    if message == "invupgrade":
        return InvUpgrade()

    prefix = message.split("/", 1)[0]

    try:
        if prefix == "connect":
            parts = _split(message, 2)
            if parts is None:
                return Unknown()
            return Connect(init_data_validator.check(parts[1]))

        if prefix == "use":
            parts = _split(message, 4)
            if parts is None:
                return Unknown()
            return Use(parts[1], int(parts[2]), int(parts[3]))

        if prefix == "collect":
            parts = _split(message, 3)
            if parts is None:
                return Unknown()
            return Collect(int(parts[1]), int(parts[2]))

        if prefix == "upgrade":
            parts = _split(message, 3)
            if parts is None:
                return Unknown()
            return Upgrade(int(parts[1]), int(parts[2]))

        if prefix == "buy":
            parts = _split(message, 3)
            if parts is None:
                return Unknown()
            return Buy(parts[1], int(parts[2]))

        if prefix == "order":
            parts = _split(message, 3)
            if parts is None:
                return Unknown()
            return OrderOperation(parts[1], int(parts[2]))

        if prefix == "place":
            parts = _split(message, 4)
            if parts is None:
                return Unknown()
            return Place(parts[1], int(parts[2]), int(parts[3]))

        if prefix == "move":
            parts = _split(message, 5)
            if parts is None:
                return Unknown()
            return Move(int(parts[1]), int(parts[2]), int(parts[3]), int(parts[4]))

        if prefix == "claim":
            parts = _split(message, 2)
            if parts is None:
                return Unknown()
            return ClaimDeposit(int(parts[1]))

        if prefix == "buyslot":
            parts = _split(message, 3)
            if parts is None:
                return Unknown()
            return PurchaseSlot(int(parts[1]), int(parts[2]))

        if prefix == "buydeal":
            parts = _split(message, 2)
            if parts is None:
                return Unknown()
            return PurchaseDeal(parts[1])

        if prefix == "activateb":
            parts = _split(message, 2)
            if parts is None:
                return Unknown()
            return ActivateBooster(int(parts[1]))

        if prefix == "rmobstacle":
            parts = _split(message, 3)
            if parts is None:
                return Unknown()
            return RemoveObstacle(int(parts[1]), int(parts[2]))

    except ValueError:
        return Unknown()

    return Unknown()
