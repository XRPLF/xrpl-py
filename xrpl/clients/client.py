"""Interface for all network clients to follow."""
from __future__ import annotations

from abc import ABC, abstractmethod

from xrpl.models.requests.request import Request
from xrpl.models.response import Response


class Client(ABC):
    """Interface for all network clients to follow."""

    def __init__(self: Client, url: str) -> None:
        """
        Constructs a Client.

        Arguments:
            url: The URL of the rippled node to submit requests to.
        """
        self.url = url

    @abstractmethod
    def request(self: Client, request_object: Request) -> Response:
        """
        Submit the request represented by the request_object to the rippled node
        specified by this client's URL.

        Arguments:
            request_object: An object representing information about a rippled request.

        Raises:
            NotImplementedError: Always.
        """
        raise NotImplementedError(f"{self.__class__.__name__}.request not implemented.")
