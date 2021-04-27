"""A client for interacting with the rippled JSON RPC."""
from __future__ import annotations

import asyncio
import json
from typing import Callable

import websockets

from xrpl.clients.client import Client
from xrpl.clients.utils import request_to_websocket, websocket_to_response
from xrpl.models.requests.request import Request
from xrpl.models.response import Response


class WebsocketClient(Client):
    """A client for interacting with the rippled WebSocket API."""

    def __init__(self: WebsocketClient, url: str) -> None:
        """
        Constructs a WebsocketClient.

        Arguments:
            url: The URL of the rippled node to submit requests to.
        """
        self.url = url
        self.websocket = None

    async def request_async(self: WebsocketClient, request_object: Request) -> Response:
        """
        Asynchronously submit the request represented by the request_object to the
        rippled node specified by this client's URL.

        Arguments:
            request_object: An object representing information about a rippled request.

        Returns:
            The response from the server, as a Response object.
        """
        formatted_request = request_to_websocket(request_object)
        if "id" not in formatted_request:
            formatted_request["id"] = "request_{}".format(formatted_request["command"])
        async with websockets.connect(self.url) as websocket:
            await websocket.send(json.dumps(formatted_request))
            response = await websocket.recv()
            response_dict = json.loads(response)
            assert response_dict["id"] == formatted_request["id"]
            return websocket_to_response(response_dict)

    def request(self: WebsocketClient, request_object: Request) -> Response:
        """
        Synchronously submit the request represented by the request_object to the
        rippled node specified by this client's URL.

        Arguments:
            request_object: An object representing information about a rippled request.

        Returns:
            The response from the server, as a Response object.
        """
        return asyncio.get_event_loop().run_until_complete(
            self.request_async(request_object)
        )

    async def listen_async(
        self: WebsocketClient,
        request_object: Request,
        handler: Callable[[Response], None],
    ) -> None:
        """
        Asynchronously submits a request represented by the request_object to the
        rippled node specified by this client's URL, and listens to (and processes) all
        responses from the server.

        Arguments:
            request_object: An object representing information about a rippled request.
            handler: The method that handles the Response objects from the server.
                Takes a Response object as a parameter and returns None.
        """
        formatted_request = request_to_websocket(request_object)
        if "id" not in formatted_request:
            formatted_request["id"] = "request_{}".format(formatted_request["command"])

        async with websockets.connect(self.url) as websocket:
            await websocket.send(json.dumps(formatted_request))
            try:
                async for message in websocket:
                    await websocket.send(json.dumps(formatted_request))
                    response = await websocket.recv()
                    response_dict = json.loads(response)
                    assert response_dict["id"] == formatted_request["id"]
                    handler(websocket_to_response(response_dict))
            except asyncio.exceptions.CancelledError:
                return

    def listen(
        self: WebsocketClient,
        request_object: Request,
        handler: Callable[[Response], None],
    ) -> None:
        """
        Synchronously submits a request represented by the request_object to the
        rippled node specified by this client's URL, and listens to (and processes) all
        responses from the server.

        Arguments:
            request_object: An object representing information about a rippled request.
            handler: The method that handles the Response objects from the server.
                Takes a Response object as a parameter and returns None.
        """
        asyncio.get_event_loop().run_until_complete(
            self.listen_async(request_object, handler)
        )
        # asyncio.get_event_loop().run_forever()

    def close(self: WebsocketClient) -> None:
        """Closes any open WebSocket connections."""
        for task in asyncio.all_tasks():
            task.cancel()
