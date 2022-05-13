"""Test the json_rpc_client."""
from __future__ import annotations

from unittest import TestCase

from xrpl.asyncio.clients.exceptions import XRPLRequestFailureException
from xrpl.clients import JsonRpcClient
from xrpl.models.requests import ServerInfo


class TestJsonRpcClient(TestCase):
    """Test json_rpc_client."""

    def test_json_rpc_client_invalid_url(self: TestJsonRpcClient) -> None:
        # Invalid URL
        JSON_RPC_URL = "https://s2.ripple.com:51233/"
        with self.assertRaises(XRPLRequestFailureException):
            client = JsonRpcClient(JSON_RPC_URL)
            client.request(ServerInfo())
