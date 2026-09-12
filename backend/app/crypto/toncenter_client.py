import httpx


class ToncenterClient:
    def __init__(self, base_url: str, api_key: str, client: httpx.AsyncClient | None = None) -> None:
        headers = {"X-API-Key": api_key} if api_key else {}
        self._client = client or httpx.AsyncClient(
            base_url=base_url.rstrip("/"), headers=headers, timeout=30.0
        )

    async def aclose(self) -> None:
        await self._client.aclose()

    async def get_seqno(self, address: str) -> int:
        response = await self._client.post(
            "/runGetMethod",
            json={"address": address, "method": "seqno", "stack": []},
        )
        response.raise_for_status()
        stack = response.json()["result"]["stack"]
        return int(stack[0][1], 16)

    async def send_boc(self, boc: str) -> None:
        response = await self._client.post("/sendBoc", json={"boc": boc})
        response.raise_for_status()
