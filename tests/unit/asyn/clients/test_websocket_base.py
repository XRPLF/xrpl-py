"""Regression tests for issue #977: a malformed JSON frame must not kill
the WebSocket handler task."""

import asyncio
import io
import json
from contextlib import redirect_stdout
from typing import List
from unittest import IsolatedAsyncioTestCase
from unittest.mock import AsyncMock, patch

from xrpl.asyncio.clients import websocket_base
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


class TestWebsocketHeaders(IsolatedAsyncioTestCase):
    """Custom header forwarding on the WebSocket handshake."""

    async def test_forwards_headers_on_connect(self) -> None:
        client = AsyncWebsocketClient(
            "ws://test", headers={"Authorization": "Bearer testtoken"}
        )

        with patch.object(
            websocket_base.websocket_client, "connect", new_callable=AsyncMock
        ) as mock_connect:
            mock_connect.return_value = _FakeWebSocket([])

            await client._do_open()

            self.assertEqual(
                mock_connect.call_args.kwargs["additional_headers"],
                {"Authorization": "Bearer testtoken"},
            )

            # _do_open spawned a handler task over the (empty) connection
            client._handler_task.cancel()

    async def test_no_headers_passes_none(self) -> None:
        client = AsyncWebsocketClient("ws://test")

        with patch.object(
            websocket_base.websocket_client, "connect", new_callable=AsyncMock
        ) as mock_connect:
            mock_connect.return_value = _FakeWebSocket([])

            await client._do_open()

            self.assertIsNone(mock_connect.call_args.kwargs["additional_headers"])

            client._handler_task.cancel()
