"""Regression tests for WebSocket handler edge cases."""

import asyncio
import io
import json
from contextlib import redirect_stdout
from typing import List
from unittest import IsolatedAsyncioTestCase

from xrpl.asyncio.clients.async_websocket_client import AsyncWebsocketClient


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

        ws = AsyncWebsocketClient("ws://test")
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

    async def test_handler_prints_malformed_frame(self) -> None:
        """The skipped frame must be surfaced on stdout so the failure is
        not silent."""
        bad_frame = b"{ this is not valid json"
        frames = [
            json.dumps({"id": "req_1", "result": "ok"}).encode(),
            bad_frame,
            json.dumps({"id": "req_2", "result": "ok"}).encode(),
        ]

        ws = AsyncWebsocketClient("ws://test")
        ws._websocket = _FakeWebSocket(frames)  # type: ignore[assignment]
        ws._messages = asyncio.Queue()
        ws._open_requests = {}

        buf = io.StringIO()
        with redirect_stdout(buf):
            await ws._handler()
        output = buf.getvalue()

        # The malformed frame's repr must appear in stdout, and the two
        # valid frames must not (only the bad one is logged).
        self.assertIn(repr(bad_frame), output)
        self.assertIn("malformed", output.lower())
        self.assertNotIn("req_1", output)
        self.assertNotIn("req_2", output)


class TestHandlerDuplicateId(IsolatedAsyncioTestCase):
    async def test_handler_survives_duplicate_id_on_done_future(self) -> None:
        """Multiple responses with the same id must not crash the handler.

        Subscription-style commands (e.g. path_find) can produce many server
        messages carrying the same id.  If the Future for that id has already
        been resolved, set_result would raise InvalidStateError and kill the
        handler task."""
        frames = [
            json.dumps({"id": "pf_1", "type": "response"}).encode(),
            json.dumps({"id": "pf_1", "type": "path_find"}).encode(),
            json.dumps({"id": "pf_1", "type": "path_find"}).encode(),
        ]

        ws = AsyncWebsocketClient("ws://test")
        ws._websocket = _FakeWebSocket(frames)  # type: ignore[assignment]
        ws._messages = asyncio.Queue()
        ws._open_requests = {
            "pf_1": asyncio.get_running_loop().create_future(),
        }

        await ws._handler()

        enqueued = []
        while not ws._messages.empty():
            enqueued.append(ws._messages.get_nowait())
        self.assertEqual(len(enqueued), 3)
        self.assertEqual(
            ws._open_requests["pf_1"].result(), {"id": "pf_1", "type": "response"}
        )
