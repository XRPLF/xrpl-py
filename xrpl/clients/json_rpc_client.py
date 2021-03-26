"""A client for interacting with the rippled JSON RPC."""

from __future__ import annotations

import requests

from xrpl.clients.client import Client
from xrpl.clients.utils import json_to_response, request_to_json_rpc
from xrpl.models.requests.request import Request
from xrpl.models.response import Response

# QUESTIONS:
# Should we have different exception types for network exceptions
# (i.e. an invalid URL) v.s. actual rippled exceptions
#   (such as maybe complaining about a malformed request, etc.)
# Will we need different exception types for the JSON RPC client v.s.
# the websockets client?  Unclear

# TODO:
# - error handling!


class JsonRpcClient(Client):
    """A client for interacting with the rippled JSON RPC."""

    def request(self: JsonRpcClient, request_object: Request) -> Response:
        """
        Submit the request represented by the request_object to the rippled node
        specified by this client's URL.

        Arguments:
            request_object: An object representing information about a rippled request.

        Returns:
            The response from the server, as a Response object.
        """
        formatted_request = request_to_json_rpc(request_object)
        response = requests.post(self.url, json=formatted_request)
        # TODO: error checking here - raise if the response from server was error?
        # OR just return a Response object with ResponseStatus.ERROR?
        return json_to_response(response.json())
