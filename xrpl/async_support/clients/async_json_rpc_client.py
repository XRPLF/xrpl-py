"""An async client for interacting with the rippled JSON RPC."""
from __future__ import annotations

from xrpl.async_support.clients.async_client import AsyncClient
from xrpl.async_support.clients.json_rpc_base import JsonRpcBase


class AsyncJsonRpcClient(AsyncClient, JsonRpcBase):
    """An async client for interacting with the rippled JSON RPC."""

    def __init__(self: AsyncJsonRpcClient, url: str) -> None:
        """
        Initialize this AsyncJsonRpcClient.

        Arguments:
            url: The url to which to connect.
        """
        self.url = url
