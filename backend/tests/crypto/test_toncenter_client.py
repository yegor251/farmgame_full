import httpx

from app.crypto.toncenter_client import ToncenterClient


def _client_with_transport(transport: httpx.MockTransport) -> ToncenterClient:
    return ToncenterClient(
        base_url="https://toncenter.com/api/v2",
        api_key="secret",
        client=httpx.AsyncClient(base_url="https://toncenter.com/api/v2", transport=transport),
    )


async def test_get_seqno_parses_hex_stack_value() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.url.path == "/api/v2/runGetMethod"
        return httpx.Response(200, json={"result": {"stack": [["num", "0x7"]]}})

    client = _client_with_transport(httpx.MockTransport(handler))

    seqno = await client.get_seqno("0:wallet")

    assert seqno == 7


async def test_send_boc_posts_boc_payload() -> None:
    received: dict[str, object] = {}

    def handler(request: httpx.Request) -> httpx.Response:
        received["json"] = request.read()
        return httpx.Response(200, json={"ok": True})

    client = _client_with_transport(httpx.MockTransport(handler))

    await client.send_boc("base64boc")

    assert b"base64boc" in received["json"]
