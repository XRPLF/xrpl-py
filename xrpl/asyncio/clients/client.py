"""Interface for all network clients to follow."""
from __future__ import annotations

from abc import ABC, abstractmethod

from xrpl.models.requests.request import Request
from xrpl.models.response import Response


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

    @abstractmethod
    async def request_impl(self: Client, request: Request) -> Response:
        """
        This is the actual driver for a given Client's request. It must be
        async because all of the helper functions in this library are
        async-first. Implement this in a given Client.

        Arguments:
            request: An object representing information about a rippled request.

        Returns:
            The response from the server, as a Response object.

        :meta private:
        """
        pass
