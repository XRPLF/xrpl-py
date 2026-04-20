"""Regression tests for issue #977: a malformed JSON frame must not kill
the WebSocket handler task."""

import asyncio
import json
from typing import List
from unittest import IsolatedAsyncioTestCase

from xrpl.asyncio.clients.websocket_base import WebsocketBase


class _ConcreteWebsocketBase(WebsocketBase):
    """Concrete subclass only needed because WebsocketBase is abstract
    (it declares _request_impl). The handler logic under test lives
    entirely in the parent; we never invoke this method."""

    async def _request_impl(  # type: ignore[no-untyped-def]
        self, request, timeout=None
    ):
        raise NotImplementedError


class _FakeWebSocket:
    """Minimal async-iterable stand-in for websockets.ClientConnection.

    Yields each frame in ``frames`` and then terminates, which lets
    ``_handler`` return normally (as it would when the server closes the
    connection cleanly)."""

    def __init__(self, frames: List[bytes]) -> None:
        self._frames = frames

    def __aiter__(self) -> "_FakeWebSocket":
        self._iter = iter(self._frames)
        return self

    async def __anext__(self) -> bytes:
        try:
            return next(self._iter)
        except StopIteration:
            raise StopAsyncIteration


class TestHandlerMalformedJson(IsolatedAsyncioTestCase):
    async def test_handler_survives_malformed_frame(self) -> None:
        """Send three frames: valid, malformed, valid. The handler must
        enqueue both valid frames and simply skip the malformed one."""
        frames = [
            json.dumps({"id": "req_1", "result": "ok"}).encode(),
            b"{ this is not valid json",
            json.dumps({"id": "req_2", "result": "ok"}).encode(),
        ]

        ws = _ConcreteWebsocketBase("ws://test")
        ws._websocket = _FakeWebSocket(frames)  # type: ignore[assignment]
        ws._messages = asyncio.Queue()
        ws._open_requests = {}

        # Must not raise. Before the fix, json.JSONDecodeError on frame 2
        # would propagate out and terminate the handler task.
        await ws._handler()

        # Both valid frames were enqueued; the malformed one was dropped.
        enqueued = []
        while not ws._messages.empty():
            enqueued.append(ws._messages.get_nowait())
        self.assertEqual(len(enqueued), 2)
        self.assertEqual(enqueued[0], {"id": "req_1", "result": "ok"})
        self.assertEqual(enqueued[1], {"id": "req_2", "result": "ok"})
