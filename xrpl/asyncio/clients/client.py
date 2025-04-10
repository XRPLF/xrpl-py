"""Interface for all network clients to follow."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Optional, Dict

from typing_extensions import Final, Self

from xrpl.asyncio.clients.exceptions import XRPLRequestFailureException
from xrpl.models.requests import ServerInfo
from xrpl.models.requests.request import Request
from xrpl.models.response import Response

# The default request timeout duration. Set in Client._request_impl to allow more time
# for longer running commands.
REQUEST_TIMEOUT: Final[float] = 10.0


class Client(ABC):
    """
    Interface for all network clients to follow.

    :meta private:
    """

    def __init__(
        self: Self,
        url: str,
        headers: Optional[Dict[str, str]] = None,
    ) -> None:
        """
        Initializes a client.

        Arguments:
            url: The URL to which this client will connect.
            headers: Optional dictionary of default headers to include with each request.
                These can be used to authenticate with private XRPL nodes or pass
                custom metadata, such as:
                - {"Authorization": "Bearer <token>"}
                - {"X-Dhali-Payment": "<claim_token>"}
        """
        self.url = url
        self.headers = headers or {}
        self.network_id: Optional[int] = None
        self.build_version: Optional[str] = None

    @abstractmethod
    async def _request_impl(
        self: Self, request: Request, *, timeout: float = REQUEST_TIMEOUT
    ) -> Response:
        """
        This is the actual driver for a given Client's request. It must be
        async because all of the helper functions in this library are
        async-first. Implement this in a given Client.

        Arguments:
            request: An object representing information about a rippled request.
            timeout: The maximum tolerable delay on waiting for a response.

        Returns:
            The response from the server, as a Response object.

        :meta private:
        """
        pass


async def get_network_id_and_build_version(client: Client) -> None:
    """
    Get the network id and build version of the connected server.

    Args:
        client: The network client to use to send the request.

    Raises:
        XRPLRequestFailureException: if the rippled API call fails.
    """
    if client.network_id and client.build_version:
        return

    response = await client._request_impl(ServerInfo())
    if response.is_successful():
        if "network_id" in response.result["info"]:
            client.network_id = response.result["info"]["network_id"]
        if not client.build_version and "build_version" in response.result["info"]:
            client.build_version = response.result["info"]["build_version"]
        return

    raise XRPLRequestFailureException(response.result)
