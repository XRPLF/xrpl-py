"""A client for interacting with the rippled JSON RPC."""
from __future__ import annotations

import asyncio
import json
from typing import Any, Dict

import websockets

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

    def __init__(self: WebsocketClient, url: str) -> None:
        """
        Constructs a WebsocketClient.

        Arguments:
            url: The URL of the rippled node to submit requests to.
        """
        self.url = url
        self.websocket = None
        self.handler_task = None
        self.open_requests = {}
        self._next_response_id = 0

    @property
    def next_response_id(self: WebsocketClient) -> int:
        ret = self._next_response_id
        self._next_response_id += 1
        return ret

    async def open_async(self: WebsocketClient) -> None:
        self.websocket = await websockets.connect(self.url)
        self.handler_task = asyncio.get_event_loop().create_task(self.handler())

    def open(self: WebsocketClient) -> None:
        return asyncio.get_event_loop().run_until_complete(self.open_async())

    async def handler(self: WebsocketClient) -> None:
        print("handler on")
        try:
            async for response in self.websocket:
                print(response)
                response_dict = json.loads(response)
                if "id" in response_dict:
                    if response_dict["id"] in self.open_requests:
                        self.open_requests[response_dict["id"]] = response_dict
                    # else:
                    #     raise XRPLWebsocketException("somehow got a non-open request")
                    # this else doesn't handle subscribe stuff
        except asyncio.CancelledError:
            pass

    async def send(self: WebsocketClient, request_object: Request) -> None:
        print(f"sending message {request_object}")
        formatted_request = request_to_websocket(request_object)
        await self.websocket.send(json.dumps(formatted_request))
        print("sent")

    async def request_async(self: WebsocketClient, request_object: Request) -> Response:
        if request_object.id is None:
            request_dict = request_object.to_dict()
            request_dict[
                "id"
            ] = f"request_{request_object.method}_{self.next_response_id}"
            print(request_dict)
            request_object = Request.from_dict(request_dict)
        if request_object.id in self.open_requests:
            raise XRPLWebsocketException("ALready have an open reqeust by that ID")
        self.open_requests[request_object.id] = None
        await self.send(request_object)
        while self.open_requests[request_object.id] is None:
            await asyncio.sleep(1)  # TODO: make this smaller
        response_dict = self.open_requests[request_object.id]
        return websocket_to_response(response_dict)

    def request(self: WebsocketClient, request_object: Request) -> Response:
        return asyncio.get_event_loop().run_until_complete(
            self.request_async(request_object)
        )

    async def close_async(self: WebsocketClient) -> None:
        """Asynchronously closes any open WebSocket connections."""
        self.handler_task.cancel()
        try:
            await self.handler_task
        except asyncio.CancelledError:
            print("main(): cancel_me is cancelled now")
        await self.websocket.close()

    def close(self: WebsocketClient) -> None:
        """Synchronously closes any open WebSocket connections."""
        asyncio.get_event_loop().create_task(self.close_async())
