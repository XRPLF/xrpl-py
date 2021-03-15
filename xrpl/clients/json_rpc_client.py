"""A client for interacting with the rippled JSON RPC."""

from __future__ import annotations

from typing import Any, Dict

import requests

from xrpl.clients.client import Client
from xrpl.models.requests.request import Request
from xrpl.models.response import Response, ResponseStatus, ResponseType

# from rippled_exception import RippledException

# QUESTIONS:
# Should we have different exception types for network exceptions
# (i.e. an invalid URL) v.s. actual rippled exceptions
#   (such as maybe complaining about a malformed request, etc.)
# Will we need different exception types for the JSON RPC client v.s.
# the websockets client?  Unclear

# TODO:
# - error handling!


def request_to_json_rpc(request_object: Request) -> Dict[str, Any]:
    """Converts a request model object to the appropriate JSON format for
    interacting with the rippled API.

    Args:
        request_object: A Request object representing the parameters of a
                        request to the rippled JSON RPC.

    Returns:
        A dictionary containing the attributes of this Request object formatted
        for submission to the rippled JSON RPC.
    """
    method = request_object.method.name.lower()
    params = request_object.to_dict()
    del params["method"]
    return {"method": method, "params": [params]}


def json_to_response(json: Dict[str, Any]) -> Response:
    """Converts a JSON response from the rippled server into a Response object.

    Args:
        json: A dictionary representing the contents of the json response from the
              rippled server.

    Returns:
        A Response object containing the information in the rippled server's response.
    """
    result = json["result"]
    raw_status = result["status"]
    if raw_status == "success":
        status = ResponseStatus.SUCCESS
    else:
        status = ResponseStatus.ERROR
    # TODO: response_type changes based on what we're getting back... where/how do we
    #  differentiate based on that?
    # TODO: should we pull fields "status" OUT of result dict?
    response_type = ResponseType.RESPONSE
    return Response(status=status, result=result, type=response_type)


class JsonRpcClient(Client):
    """A client for interacting with the rippled JSON RPC."""

    def request(self: JsonRpcClient, request_object: Request) -> Response:
        """
        Submit the request represented by the request_object to the rippled node
        specified by this client's URL.

        Arguments:
            request_object: An object representing information about a rippled request.

        Returns:
            The response from the server, as a Response object, if successful.
        """
        formatted_request = request_to_json_rpc(request_object)
        response = requests.post(self.url, json=formatted_request)
        # TODO: error checking here - raise if the response from server was error?
        # OR just return a Response object with ResponseStatus.ERROR?
        return json_to_response(response.json())
