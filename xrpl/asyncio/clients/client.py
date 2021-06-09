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

    url: str

    @abstractmethod
    async def request_impl(self: Client, request: Request) -> Response:
        """
        This is the actual driver for a given Client's request. It must be
        async because all of the helper functions in this library are
        async-first. Implement this in a given Client.

        Arguments:
            request: The Request to send.

        Raises:
            NotImplementedError: always.
        """
        raise NotImplementedError(
            f"{self.__class__.__name__}.request_impl not implemented."
        )
