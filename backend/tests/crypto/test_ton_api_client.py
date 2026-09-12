import httpx

from app.crypto.ton_api_client import TonApiClient


def _client_with_transport(transport: httpx.MockTransport) -> TonApiClient:
    return TonApiClient(
        base_url="https://tonapi.io",
        api_key="secret",
        client=httpx.AsyncClient(base_url="https://tonapi.io", transport=transport),
    )


async def test_get_account_events_parses_response() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.url.path == "/v2/accounts/0:acc/events"
        assert request.url.params["limit"] == "100"
        assert request.url.params["start_date"] == "0"
        return httpx.Response(
            200,
            json={
                "events": [
                    {
                        "event_id": "1a",
                        "timestamp": 111,
                        "actions": [
                            {
                                "TonTransfer": {
                                    "recipient": {"address": "0:acc"},
                                    "amount": 500,
                                    "comment": "7",
                                }
                            }
                        ],
                    }
                ]
            },
        )

    client = _client_with_transport(httpx.MockTransport(handler))

    events = await client.get_account_events("0:acc", limit=100, start_date=0)

    assert len(events) == 1
    assert events[0].event_id == "1a"
    assert events[0].actions[0].TonTransfer is not None
    assert events[0].actions[0].TonTransfer.amount == 500


async def test_get_jetton_wallet_address_returns_none_on_404() -> None:
    client = _client_with_transport(httpx.MockTransport(lambda request: httpx.Response(404)))

    address = await client.get_jetton_wallet_address("0:acc", "0:jetton")

    assert address is None


async def test_get_jetton_wallet_address_returns_address() -> None:
    handler = httpx.MockTransport(
        lambda request: httpx.Response(200, json={"wallet_address": {"address": "0:wallet"}})
    )
    client = _client_with_transport(handler)

    address = await client.get_jetton_wallet_address("0:acc", "0:jetton")

    assert address == "0:wallet"
