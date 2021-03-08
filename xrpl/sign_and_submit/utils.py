"""TODO: docstring"""

from xrpl.models.response import Response, ResponseStatus, ResponseType


def json_to_response(json: dict) -> Response:
    """Converts a JSON response from the rippled server into a Response object."""
    result = json["result"]
    raw_status = result["status"]
    if raw_status == "success":
        status = ResponseStatus.SUCCESS
    else:
        status = ResponseStatus.ERROR
    try:
        response_id = result["id"]
    except KeyError:
        response_id = None
    # TODO: response_type changes based on what we're getting back... where/how do we
    #  differentiate based on that?
    # TODO: should we pull fields "status" OUT of result dict? (and maybe "id" too if
    # that's where it lives)
    response_type = ResponseType.RESPONSE
    return Response(status=status, result=result, id=response_id, type=response_type)
