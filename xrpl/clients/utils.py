"""Helper functions for the clients module."""

from typing import Any, Dict

from xrpl.models.requests.request import Request
from xrpl.models.response import Response, ResponseStatus, ResponseType


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
    del result["status"]
    # TODO: response_type changes based on what we're getting back... where/how do we
    #  differentiate based on that?
    # TODO: should we pull fields "status" OUT of result dict?
    response_type = ResponseType.RESPONSE
    return Response(status=status, result=result, type=response_type)
