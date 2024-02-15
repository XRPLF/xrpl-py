"""Interface for all network clients to follow."""
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Optional

from typing_extensions import Final

from xrpl.models.requests.request import Request
from xrpl.models.response import Response

# The default request timeout duration. If you need more time, please pass the required
# value into the Client._request_impl function
_TIMEOUT: Final[float] = 10.0


class Client(ABC):
    """
    Interface for all network clients to follow.

    :meta private:
    """

    def __init__(self: Client, url: str) -> None:
        """
        Initializes a client.

        Arguments:
            url: The url to which this client will connect
        """
        self.url = url
        self.network_id: Optional[int] = None
        self.build_version: Optional[str] = None

    @abstractmethod
    async def _request_impl(
        self: Client, request: Request, *, timeout: Optional[float] = _TIMEOUT
    ) -> Response:
        """
        This is the actual driver for a given Client's request. It must be
        async because all of the helper functions in this library are
        async-first. Implement this in a given Client.

        Arguments:
            request: An object representing information about a rippled request.
            timeout: The maximum tolerable delay on waiting for a response.
                Note: Optional is used in the type in order to honor the existing
                behavior in certain overridden functions. WebsocketBase.do_request_impl
                waits indefinitely for the completion of a request, whereas
                JsonRpcBase._request_impl waits for 10 seconds before timing out a
                request.

        Returns:
            The response from the server, as a Response object.

        :meta private:
        """
        pass
