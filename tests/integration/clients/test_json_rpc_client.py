"""Test the json_rpc_client."""
from __future__ import annotations

from unittest import TestCase

from xrpl.clients import JsonRpcClient
from xrpl.models.requests import ServerInfo


class TestJsonRpcClient(TestCase):
    """Test json_rpc_client."""

    def test_json_rpc_client_valid_url(self: TestJsonRpcClient) -> None:
        # Valid URL
        JSON_RPC_URL = "https://s.altnet.rippletest.net:51234"
        client = JsonRpcClient(JSON_RPC_URL)
        client.request(ServerInfo())
