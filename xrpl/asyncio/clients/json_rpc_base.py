"""A common interface for JsonRpc requests."""

from __future__ import annotations

from json import JSONDecodeError
from typing import Optional, Dict

from httpx import AsyncClient
from typing_extensions import Self

from xrpl.asyncio.clients.client import REQUEST_TIMEOUT, Client
from xrpl.asyncio.clients.exceptions import XRPLRequestFailureException
from xrpl.asyncio.clients.utils import json_to_response, request_to_json_rpc
from xrpl.models.requests.request import Request
from xrpl.models.response import Response


class JsonRpcBase(Client):
    """
    A common interface for JsonRpc requests.

    :meta private:
    """

    def __init__(
        self: Self,
        url: str,
        *,
        headers: Optional[Dict[str, str]] = None,
    ) -> None:
        """
        Initializes a new JsonRpcBase client.

        Arguments:
            url: The URL of the XRPL node to connect to.
            headers: Optional default headers for all requests (e.g. API key or Dhali payment-claim).
        """
        super().__init__(url)
        self.headers = headers or {}

    async def _request_impl(
        self: Self,
        request: Request,
        *,
        timeout: float = REQUEST_TIMEOUT,
        headers: Optional[Dict[str, str]] = None,
    ) -> Response:
        """
        Base ``_request_impl`` implementation for JSON RPC.

        Arguments:
            request: An object representing information about a rippled request.
            timeout: The duration within which we expect to hear a response from the
                rippled server.
            headers: Optional additional headers to include for this request.

        Returns:
            The response from the server, as a Response object.

        Raises:
            XRPLRequestFailureException: if response can't be JSON decoded.

        :meta private:
        """
        # Merge global and per-request headers
        merged_headers = {
            "Content-Type": "application/json",
            **self.headers,
            **(headers or {}),
        }

        async with AsyncClient(timeout=timeout) as http_client:
            response = await http_client.post(
                self.url,
                json=request_to_json_rpc(request),
                headers=merged_headers,
            )
            try:
                return json_to_response(response.json())
            except JSONDecodeError:
                raise XRPLRequestFailureException(
                    {
                        "error": response.status_code,
                        "error_message": response.text,
                    }
                ) from None