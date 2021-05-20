"""A client for interacting with the rippled WebSocket API."""
from __future__ import annotations

from collections.abc import AsyncIterator
from types import TracebackType
from typing import Any, Dict, Type

from xrpl.asyncio.clients.async_client import AsyncClient
from xrpl.asyncio.clients.exceptions import XRPLWebsocketException
from xrpl.asyncio.clients.websocket_base import WebsocketBase
from xrpl.models.requests.request import Request


class AsyncWebsocketClient(AsyncClient, WebsocketBase):
    """A client for interacting with the rippled WebSocket API."""

    async def open(self: AsyncWebsocketClient) -> None:
        """Connects the client to the Web Socket API at the given URL."""
        await self._do_open()

    async def close(self: AsyncWebsocketClient) -> None:
        """Closes the connection."""
        await self._do_close()

    async def __aenter__(self: AsyncWebsocketClient) -> AsyncWebsocketClient:
        """
        Enters an async context after opening itself.

        Returns:
            The opened client.
        """
        await self.open()
        return self

    async def __aexit__(
        self: AsyncWebsocketClient,
        _exc_type: Type[BaseException],
        _exc_val: BaseException,
        _trace: TracebackType,
    ) -> None:
        """Exits an async context after closing itself."""
        await self.close()

    async def __aiter__(self: AsyncWebsocketClient) -> AsyncIterator[Dict[str, Any]]:
        """Iterate on received messages."""
        while self.is_open():
            yield await self._do_pop_message()

    async def send(self: AsyncWebsocketClient, request: Request) -> None:
        """
        Submit the request represented by the request to the
        rippled node specified by this client's URL.

        Arguments:
            request: A Request object representing information about a rippled request.

        Raises:
            XRPLWebsocketException: If there is already an open request by the
                request's ID, or if this WebsocketBase is not open.
        """
        if not self.is_open():
            raise XRPLWebsocketException("Websocket is not open")

        await self._do_send(request)
