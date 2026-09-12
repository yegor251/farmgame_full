import httpx

from app.crypto.ton_api_models import AccountEvent, AccountEventsResponse, JettonBalanceResponse


class TonApiClient:
    def __init__(self, base_url: str, api_key: str, client: httpx.AsyncClient | None = None) -> None:
        headers = {"Authorization": f"Bearer {api_key}"} if api_key else {}
        self._client = client or httpx.AsyncClient(
            base_url=base_url.rstrip("/"), headers=headers, timeout=30.0
        )

    async def aclose(self) -> None:
        await self._client.aclose()

    async def get_account_events(
        self, account_id: str, limit: int, start_date: int
    ) -> list[AccountEvent]:
        response = await self._client.get(
            f"/v2/accounts/{account_id}/events",
            params={"limit": limit, "start_date": start_date},
        )
        response.raise_for_status()
        return AccountEventsResponse.model_validate(response.json()).events

    async def get_jetton_wallet_address(self, account_id: str, jetton_id: str) -> str | None:
        response = await self._client.get(f"/v2/accounts/{account_id}/jettons/{jetton_id}")
        if response.status_code == httpx.codes.NOT_FOUND:
            return None
        response.raise_for_status()
        return JettonBalanceResponse.model_validate(response.json()).wallet_address.address
