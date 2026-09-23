class ClientInfo:
    def __init__(self, tg_id: int, ref_id: int) -> None:
        self.tg_id = tg_id
        self.ref_id = ref_id
        self.banned: bool = False
        self.strikes: int = 0
        self.referrals: list[int] = []
