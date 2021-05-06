"""A client for interacting with the rippled JSON RPC."""
from __future__ import annotations

import json
from asyncio import Future, Task, create_task, get_event_loop, get_running_loop
from random import randrange
from typing import Any, Callable, Dict, Optional, Union, cast

from typing_extensions import Final
from websockets.legacy.client import connect

from xrpl.clients.client import Client
from xrpl.clients.exceptions import XRPLWebsocketException
from xrpl.clients.utils import request_to_websocket, websocket_to_response
from xrpl.models.requests.request import Request
from xrpl.models.response import Response

_REQ_ID_MAX: Final[int] = 1_000_000


def _inject_request_id(request: Request) -> Request:
    if request.id is not None:
        return request
    request_dict = request.to_dict()
    request_dict["id"] = f"{request.method}_{randrange(_REQ_ID_MAX)}"
    return cast(Request, Request.from_dict(request_dict))


class WebsocketClient(Client):
    """A client for interacting with the rippled WebSocket API."""

    def __init__(
        self: WebsocketClient,
        url: str,
        response_handler: Optional[Callable[[Dict[str, Any]], None]] = None,
    ) -> None:
        """
        Constructs a WebsocketClient.

        Arguments:
            url: The URL of the rippled node to submit requests to.
            response_handler: A callback method to process all responses from the
                server, including the responses from endpoints that send periodic
                additional responses, such as `subscribe`.
        """
        self.url = url
        self.response_handler = response_handler
        self._handler_task: Optional[Task[None]] = None
        self._open_requests: Dict[str, Future[Dict[str, Any]]] = {}

    def is_open(self: WebsocketClient) -> bool:
        """
        Returns whether the Websocket client is currently open.

        Returns:
            Whether the Websocket client is currently open.
        """
        return self._handler_task is not None

    async def open_async(self: WebsocketClient) -> None:
        """
        Asynchronously connects the client to the Web Socket API at the given URL.

        Raises:
            XRPLWebsocketException: If the Websocket is already open.
        """
        if self.is_open():
            raise XRPLWebsocketException("Already open")
        self.websocket = await connect(self.url)
        self._handler_task = create_task(self._handler())

    def open(self: WebsocketClient) -> None:
        """Synchronously connects the client to the Web Socket API at the given URL."""
        get_event_loop().run_until_complete(self.open_async())

    async def _handler(self: WebsocketClient) -> None:
        async for response in self.websocket:
            response_dict = json.loads(response)
            if "id" in response_dict and response_dict["id"] in self._open_requests:
                self._open_requests[response_dict["id"]].set_result(response_dict)

            if self.response_handler is not None:
                self.response_handler(response_dict)

    def _ensure_future(self: WebsocketClient, request_id: Union[str, int]) -> None:
        str_id = str(request_id)
        if str_id not in self._open_requests:
            self._open_requests[str_id] = get_running_loop().create_future()
        elif self._open_requests[str_id].done():
            raise XRPLWebsocketException(f"Request {str_id} is already completed")

    async def send(self: WebsocketClient, request_object: Request) -> None:
        """
        Asynchronously submit the request represented by the request_object to the
        rippled node specified by this client's URL.

        Arguments:
            request_object: An object representing information about a rippled request.

        Raises:
            XRPLWebsocketException: If the Websocket is not open or the there is
                already an open request by the request_object's ID.
        """
        if not self.is_open():
            raise XRPLWebsocketException("Websocket is not open")

        request_with_id = _inject_request_id(request_object)
        assert request_with_id.id is not None  # mypy
        self._ensure_future(request_with_id.id)

        formatted_request = request_to_websocket(request_with_id)
        self.websocket.send(json.dumps(formatted_request))

    async def request_async(self: WebsocketClient, request_object: Request) -> Response:
        """
        Asynchronously submits the request represented by the request_object to the
        rippled node specified by this client's URL and waits for a response.

        Note: if this is used for an API method that returns many responses, such as
        `subscribe`, this method only returns the first response; all subsequent
        responses will be processed by the `response_handler` passed in the `__init__`
        method.

        Arguments:
            request_object: An object representing information about a rippled request.

        Returns:
            The response from the server, as a Response object.

        Raises:
            XRPLWebsocketException: If there is already an open request by the
                request_object's ID.
        """
        request_with_id = _inject_request_id(request_object)
        assert request_with_id.id is not None  # mypy
        self._ensure_future(request_with_id.id)

        create_task(self.send(request_with_id))
        raw_response = await self._open_requests[str(request_with_id.id)]
        return websocket_to_response(raw_response)

    def request(self: WebsocketClient, request_object: Request) -> Response:
        """
        Synchronously submits the request represented by the request_object to the
        rippled node specified by this client's URL and waits for a response.

        Note: if this is used for an API method that returns many responses, such as
        `subscribe`, this method only returns the first response; all subsequent
        responses will be processed by the `response_handler` passed in the `__init__`
        method.

        Arguments:
            request_object: An object representing information about a rippled request.

        Returns:
            The response from the server, as a Response object.

        Raises:
            XRPLWebsocketException: If there is already an open request by the
                request_object's ID.
        """
        return get_event_loop().run_until_complete(self.request_async(request_object))

    async def close_async(self: WebsocketClient) -> None:
        """
        Asynchronously closes the connection.

        Raises:
            XRPLWebsocketException: If the Websocket is already closed.
        """
        if not self.is_open():
            raise XRPLWebsocketException("Websocket is not open")
        await self.websocket.close()
        assert self._handler_task is not None  # mypy
        self._handler_task.cancel()
        self._handler_task = None

    def close(self: WebsocketClient) -> None:
        """
        Synchronously closes the connection.

        Raises:
            XRPLWebsocketException: If the Websocket is already closed.
        """
        get_event_loop().run_until_complete(self.close_async())
