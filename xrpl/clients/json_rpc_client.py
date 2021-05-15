"""A sync client for interacting with the rippled JSON RPC."""
from __future__ import annotations

from xrpl.async_support.clients.json_rpc_base import JsonRpcBase
from xrpl.clients.sync_client import SyncClient


class JsonRpcClient(SyncClient, JsonRpcBase):
    """A sync client for interacting with the rippled JSON RPC."""

    def __init__(self: JsonRpcClient, url: str) -> None:
        """
        Initialize this JsonRpcClient.

        Arguments:
            url: The url to which to connect.
        """
        self.url = url
