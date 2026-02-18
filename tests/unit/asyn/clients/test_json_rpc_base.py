from unittest.mock import AsyncMock, patch

import pytest
from httpx import Response

from xrpl.asyncio.clients.exceptions import XRPLAuthenticationException
from xrpl.asyncio.clients.json_rpc_base import JsonRpcBase
from xrpl.models.requests import ServerInfo


@pytest.mark.asyncio
async def test_global_headers_are_sent():
    client = JsonRpcBase(
        "https://xrpl.fake", headers={"Authorization": "Bearer testtoken"}
    )

    with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post:
        mock_post.return_value = Response(
            status_code=200,
            json={"result": {"status": "success"}, "id": 1},
        )

        await client._request_impl(ServerInfo())

        headers_sent = mock_post.call_args.kwargs["headers"]
        assert headers_sent["Authorization"] == "Bearer testtoken"
        assert headers_sent["Content-Type"] == "application/json"


@pytest.mark.asyncio
async def test_per_request_headers_override_global():
    client = JsonRpcBase(
        "https://xrpl.fake", headers={"Authorization": "Bearer default"}
    )

    with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post:
        mock_post.return_value = Response(
            status_code=200,
            json={"result": {"status": "success"}, "id": 1},
        )

        await client._request_impl(
            ServerInfo(), headers={"Authorization": "Bearer override"}
        )

        headers_sent = mock_post.call_args.kwargs["headers"]
        assert headers_sent["Authorization"] == "Bearer override"


@pytest.mark.asyncio
async def test_no_headers_does_not_crash():
    client = JsonRpcBase("https://xrpl.fake")

    with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post:
        mock_post.return_value = Response(
            status_code=200,
            json={"result": {"status": "success"}, "id": 1},
        )

        await client._request_impl(ServerInfo())

        headers_sent = mock_post.call_args.kwargs["headers"]
        assert headers_sent["Content-Type"] == "application/json"


@pytest.mark.asyncio
async def test_raises_on_401_403():
    client = JsonRpcBase("https://xrpl.fake")

    for code in [401, 403]:
        with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post:
            mock_post.return_value = Response(status_code=code, text="Unauthorized")

            with pytest.raises(
                XRPLAuthenticationException, match="Authentication failed"
            ):
                await client._request_impl(ServerInfo())
