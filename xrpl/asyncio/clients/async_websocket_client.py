"""A client for interacting with the rippled WebSocket API."""
from __future__ import annotations

from asyncio import Queue
from collections.abc import AsyncIterator
from types import TracebackType
from typing import Any, Dict, Type

from xrpl.asyncio.clients.async_client import AsyncClient
from xrpl.asyncio.clients.websocket_base import WebsocketBase
from xrpl.models.requests.request import Request


class AsyncWebsocketClient(AsyncClient, WebsocketBase):
    """A client for interacting with the rippled WebSocket API."""

    def __init__(self: AsyncWebsocketClient, url: str) -> None:
        """
        Constructs a AsyncWebsocketClient.

        Arguments:
            url: The URL of the rippled node to submit requests to.
        """
        self.url = url
        super().__init__()

    def is_open(self: AsyncWebsocketClient) -> bool:
        """
        Returns whether the AsyncWebsocket client is currently open.

        Returns:
            Whether the AsyncWebsocket client is currently open.
        """
        return self._messages is not None and super().is_open()

    async def open(self: AsyncWebsocketClient) -> None:
        """
        Connects the client to the Web Socket API at the given URL.

        Raises:
            XRPLWebsocketException: If the AsyncWebsocket is already open.
        """
        self._messages = Queue()
        await self._do_open()

    async def close(self: AsyncWebsocketClient) -> None:
        """
        Closes the connection.

        Raises:
            XRPLWebsocketException: If the AsyncWebsocket is already closed.
        """
        await self._do_close()
        # clear the message queue
        assert self._messages is not None  # mypy
        for _ in range(self._messages.qsize()):
            self._messages.get_nowait()
            self._messages.task_done()
        self._messages = None

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
            assert self._messages is not None

            # wait for the next message on the message queue
            message = await self._messages.get()
            self._messages.task_done()
            yield message

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
        await self._do_send(request)
