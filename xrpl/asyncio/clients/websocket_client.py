"""A client for interacting with the rippled JSON RPC."""
from __future__ import annotations

import asyncio
import json
from typing import Any, Callable, Dict, Optional, Union, cast

from websockets.legacy.client import connect

from xrpl.clients.client import Client
from xrpl.clients.exceptions import XRPLWebsocketException
from xrpl.clients.utils import request_to_websocket, websocket_to_response
from xrpl.models.requests.request import Request
from xrpl.models.response import Response


def _check_ids(request_dict: Dict[str, Any], response_dict: Dict[str, Any]) -> None:
    if request_dict["id"] != response_dict["id"]:
        raise XRPLWebsocketException(
            "ID of the response does not match ID of the request"
        )


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

        self._open_requests: Dict[Union[str, int], Optional[Dict[str, Any]]] = {}
        self._next_response_id = 0
        self._open = False

    @property
    def next_response_id(self: WebsocketClient) -> int:
        """
        The next response ID number. Incremented under the hood so that each ID can be
        unique without the user needing to do that by hand.

        Returns:
            The next valid response ID number.
        """
        ret = self._next_response_id
        self._next_response_id += 1
        return ret

    @property
    def is_open(self: WebsocketClient) -> bool:
        """
        Returns whether the Websocket client is currently open.

        Returns:
            Whether the Websocket client is currently open.
        """
        return self._open

    async def open_async(self: WebsocketClient) -> None:
        """Asynchronously connects the client to the Web Socket API at the given URL."""
        self.websocket = await connect(self.url)
        self._handler_task = asyncio.get_event_loop().create_task(self._handler())
        self._open = True

    def open(self: WebsocketClient) -> None:
        """Synchronously connects the client to the Web Socket API at the given URL."""
        asyncio.get_event_loop().run_until_complete(self.open_async())

    async def _handler(self: WebsocketClient) -> None:
        async for response in self.websocket:
            response_dict = json.loads(response)
            if "id" in response_dict and response_dict["id"] in self._open_requests:
                self._open_requests[response_dict["id"]] = response_dict

            if self.response_handler is not None:
                self.response_handler(response_dict)

    async def send(self: WebsocketClient, request_object: Request) -> None:
        """
        Asynchronously submit the request represented by the request_object to the
        rippled node specified by this client's URL.

        Arguments:
            request_object: An object representing information about a rippled request.

        Raises:
            XRPLWebsocketException: If the Websocket is not open.
        """
        if not self._open:
            raise XRPLWebsocketException("Websocket is not open")
        formatted_request = request_to_websocket(request_object)
        await self.websocket.send(json.dumps(formatted_request))

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
        if request_object.id is None:
            request_dict = request_object.to_dict()
            request_dict[
                "id"
            ] = f"request_{request_object.method}_{self.next_response_id}"
            request_object = cast(Request, Request.from_dict(request_dict))

        if request_object.id in self._open_requests:
            raise XRPLWebsocketException("Already have an open request by that ID")

        assert request_object.id is not None  # for mypy
        self._open_requests[request_object.id] = None

        await self.send(request_object)
        while self._open_requests[request_object.id] is None:
            await asyncio.sleep(1)  # TODO: make this smaller

        response_dict = self._open_requests[request_object.id]
        return websocket_to_response(cast(Dict[str, Any], response_dict))

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
        """
        return asyncio.get_event_loop().run_until_complete(
            self.request_async(request_object)
        )

    async def close_async(self: WebsocketClient) -> None:
        """Asynchronously closes any open WebSocket connections."""
        await self.websocket.close()
        self._handler_task.cancel()
        self._open = False

    def close(self: WebsocketClient) -> None:
        """Synchronously closes any open WebSocket connections."""
        asyncio.get_event_loop().create_task(self.close_async())
