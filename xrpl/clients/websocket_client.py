"""A sync client for interacting with the rippled WebSocket API."""
from __future__ import annotations

from asyncio import AbstractEventLoop, new_event_loop, run_coroutine_threadsafe
from concurrent.futures import CancelledError, TimeoutError
from threading import Thread
from types import TracebackType
from typing import Any, Dict, Iterator, Optional, Type, Union

from xrpl.asyncio.clients.exceptions import XRPLWebsocketException
from xrpl.asyncio.clients.websocket_base import WebsocketBase
from xrpl.clients.sync_client import SyncClient
from xrpl.models.requests.request import Request
from xrpl.models.response import Response


class WebsocketClient(SyncClient, WebsocketBase):
    """A sync client for interacting with the rippled WebSocket API."""

    def __init__(
        self: WebsocketClient, url: str, timeout: Optional[Union[int, float]] = None
    ) -> None:
        """
        Constructs a WebsocketClient.

        Arguments:
            url: The URL of the rippled node to submit requests to.
            timeout: Maximum seconds to wait for a new message when
                iterating. A value of 0 or None will result in no limit.
                If this limit is met, iteration will stop.
        """
        self.timeout = timeout
        self._loop: Optional[AbstractEventLoop] = None
        self._thread: Optional[Thread] = None
        super().__init__(url)

    def is_open(self: WebsocketClient) -> bool:
        """
        Returns whether the WebsocketClient is currently open.

        Returns:
            Whether the WebsocketClient is currently open.
        """
        return self._loop is not None and self._thread is not None and super().is_open()

    def open(self: WebsocketClient) -> None:
        """
        Connects the client to the Web Socket API at the given URL.

        Raises:
            XRPLWebsocketException: If the AsyncWebsocket is already open.
        """
        self._loop = new_event_loop()
        self._thread = Thread(
            target=self._loop.run_forever,
            daemon=True,
        )
        self._thread.start()
        run_coroutine_threadsafe(self._do_open(), self._loop).result()

    def close(self: WebsocketClient) -> None:
        """Closes the connection."""
        if not self.is_open():
            return

        assert self._loop is not None  # mypy
        assert self._thread is not None  # mypy
        run_coroutine_threadsafe(self._do_close(), self._loop).result()
        self._loop.call_soon_threadsafe(self._loop.stop)
        self._thread.join()
        self._loop = None
        self._thread = None

    def __enter__(self: WebsocketClient) -> WebsocketClient:
        """
        Enters a context after opening itself.

        Returns:
            The opened client.
        """
        self.open()
        return self

    def __exit__(
        self: WebsocketClient,
        _exc_type: Type[BaseException],
        _exc_val: BaseException,
        _trace: TracebackType,
    ) -> None:
        """Exits a context after closing itself."""
        self.close()

    def __iter__(self: WebsocketClient) -> Iterator[Dict[str, Any]]:
        """
        Iterate on received messages. This iterator will block until
        a message is received. If no message is received within
        `self.timeout` seconds then the iterator will exit. If
        `self.timeout` is `None` or `0` then the iterator will block
        indefinetly for the next messsage.
        """
        while self.is_open():
            assert self._loop is not None  # mypy
            future = run_coroutine_threadsafe(self._do_pop_message(), self._loop)
            try:
                yield future.result(self.timeout)
            except TimeoutError:
                future.cancel()
                break
            except CancelledError:
                break

    def send(self: WebsocketClient, request: Request) -> None:
        """
        Submit the request represented by the request to the
        rippled node specified by this client's URL.

        Arguments:
            request: A Request object representing information about a rippled request.

        Raises:
            XRPLWebsocketException: If there is already an open request by the
                request's ID, or if this WebsocketClient is not open.
        """
        if not self.is_open():
            raise XRPLWebsocketException("Websocket is not open")

        assert self._loop is not None  # mypy
        run_coroutine_threadsafe(self._do_send(request), self._loop).result()

    async def request_impl(self: WebsocketClient, request: Request) -> Response:
        """
        Asynchronously submits the request represented by the request to the
        rippled node specified by this client's URL and waits for a response.

        Note: if this is used for an API method that returns many responses, such as
        `subscribe`, this method only returns the first response; all subsequent
        responses will be available if you use the async iterator pattern on this
        client, IE `async for message in client`. You can create an async task to
        read messages from subscriptions.

        Arguments:
            request: An object representing information about a rippled request.

        Returns:
            The response from the server, as a Response object.

        Raises:
            XRPLWebsocketException: If there is already an open request by the
                request's ID, or if this WebsocketClient is not open.
        """
        if not self.is_open():
            raise XRPLWebsocketException("Websocket is not open")

        assert self._loop is not None  # mypy
        return run_coroutine_threadsafe(
            super().request_impl(request),
            self._loop,
        ).result()
