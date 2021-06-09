"""A client for interacting with the rippled WebSocket API."""
from __future__ import annotations

import json
from asyncio import Future, Queue, Task, create_task, get_running_loop
from random import randrange
from typing import Any, Dict, Optional

from typing_extensions import Final
from websockets.legacy.client import WebSocketClientProtocol, connect

from xrpl.asyncio.clients.client import Client
from xrpl.asyncio.clients.exceptions import XRPLWebsocketException
from xrpl.asyncio.clients.utils import request_to_websocket, websocket_to_response
from xrpl.models.requests.request import Request
from xrpl.models.response import Response

_REQ_ID_MAX: Final[int] = 1_000_000


def _inject_request_id(request: Request) -> Request:
    """
    Given a Request with an ID, return the same Request.

    Given a Request without an ID, make a copy with a randomly generated ID.
    """
    if request.id is not None:
        return request
    request_dict = request.to_dict()
    request_dict["id"] = f"{request.method}_{randrange(_REQ_ID_MAX)}"
    resp = Request.from_dict(request_dict)
    assert resp.id is not None  # mypy
    return resp


class WebsocketBase(Client):
    """
    A client for interacting with the rippled WebSocket API.

    :meta private:
    """

    def __init__(self: WebsocketBase, url: str) -> None:
        """
        Constructs a WebsocketBase.

        Arguments:
            url: The URL of the rippled node to submit requests to.
        """
        self.url = url
        self._open_requests: Dict[str, Future[Dict[str, Any]]] = {}
        self._websocket: Optional[WebSocketClientProtocol] = None
        self._handler_task: Optional[Task[None]] = None
        self._messages: Optional[Queue[Dict[str, Any]]] = None

    def is_open(self: WebsocketBase) -> bool:
        """
        Returns whether the client is currently open.

        Returns:
            Whether the client is currently open.
        """
        return (
            self._handler_task is not None
            and self._messages is not None
            and self._websocket is not None
            and self._websocket.open
        )

    async def _do_open(self: WebsocketBase) -> None:
        """Connects the client to the Web Socket API at the given URL."""
        if self.is_open():
            return

        # open the connection
        self._websocket = await connect(self.url)

        # make a message queue
        self._messages = Queue()

        # start the handler
        self._handler_task = create_task(self._handler())

    async def _do_close(self: WebsocketBase) -> None:
        """Closes the connection."""
        if not self.is_open():
            return
        assert self._handler_task is not None  # mypy
        assert self._websocket is not None  # mypy
        assert self._messages is not None  # mypy

        # cancel the handler
        self._handler_task.cancel()
        self._handler_task = None

        # cancel any pending request Futures
        for future in self._open_requests.values():
            future.cancel()
        self._open_requests = {}

        # clear the message queue
        for _ in range(self._messages.qsize()):
            self._messages.get_nowait()
            self._messages.task_done()
        self._messages = None

        # close the connection
        await self._websocket.close()

    async def _handler(self: WebsocketBase) -> None:
        """
        This is basically a middleware for the websocket library. For all received
        messages we check whether there is an outstanding future we need to resolve,
        and if so do so.

        Then we store the already-parsed JSON in our own queue for generic iteration.

        As long as a given client remains open, this handler will be running as a Task.
        """
        assert self._websocket is not None  # mypy
        assert self._messages is not None  # mypy
        async for response in self._websocket:
            response_dict = json.loads(response)

            # if this response corresponds to request, fulfill the Future
            if "id" in response_dict and response_dict["id"] in self._open_requests:
                self._open_requests[response_dict["id"]].set_result(response_dict)

            # enqueue the response for the message queue
            self._messages.put_nowait(response_dict)

    def _set_up_future(self: WebsocketBase, request: Request) -> None:
        """
        Only to be called from the public send and request_impl functions.
        Given a request with an ID, ensure that that ID is backed by an open
        Future in self._open_requests.
        """
        if request.id is None:
            return
        request_str = str(request.id)
        if (
            request_str in self._open_requests
            and not self._open_requests[request_str].done()
        ):
            raise XRPLWebsocketException(
                f"Request {request_str} is already in progress."
            )
        self._open_requests[request_str] = get_running_loop().create_future()

    async def _do_send_no_future(self: WebsocketBase, request: Request) -> None:
        assert self._websocket is not None  # mypy
        await self._websocket.send(
            json.dumps(
                request_to_websocket(request),
            ),
        )

    async def _do_send(self: WebsocketBase, request: Request) -> None:
        # we need to set up a future here, even if no one cares about it, so
        # that if a user submits a few requests with the same ID they fail.
        self._set_up_future(request)
        await self._do_send_no_future(request)

    async def _do_pop_message(self: WebsocketBase) -> Dict[str, Any]:
        assert self._messages is not None  # mypy
        msg = await self._messages.get()
        self._messages.task_done()
        return msg

    async def request_impl(self: WebsocketBase, request: Request) -> Response:
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
                request's ID, or if this WebsocketBase is not open.

        :meta private:
        """
        if not self.is_open():
            raise XRPLWebsocketException("Websocket is not open")

        # if no ID on this request, generate and inject one, and ensure it
        # is backed by a future
        request_with_id = _inject_request_id(request)
        request_str = str(request_with_id.id)
        self._set_up_future(request_with_id)

        # fire-and-forget the send, and await the Future
        create_task(self._do_send_no_future(request_with_id))
        raw_response = await self._open_requests[request_str]

        # remove the resolved Future, hopefully getting it garbage colleted
        del self._open_requests[request_str]
        return websocket_to_response(raw_response)
