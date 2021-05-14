"""Interface for all network clients to follow."""
from __future__ import annotations

from abc import ABC, abstractmethod

from xrpl.models.requests.request import Request
from xrpl.models.response import Response


class Client(ABC):
    """Interface for all network clients to follow."""

    def __init__(self: Client, url: str) -> None:
        """
        Initialize this Client.

        Arguments:
            url: The url to which to connect.
        """
        self.url = url

    @abstractmethod
    async def request_async(
        self: Client, request_object: Request
    ) -> Response:  # noqa: D102
        raise NotImplementedError(f"{self.__class__.__name__}.request not implemented.")

    @abstractmethod
    def request(self: Client, request_object: Request) -> Response:  # noqa: D102
        raise NotImplementedError(f"{self.__class__.__name__}.request not implemented.")
