"""Helper functions for the Models package."""
from typing import Any, Dict, NewType, Union

from xrpl.models.base_model import BaseModel

_JSON_Primatives = NewType("_JSON_Primatives", Union[int, float, str])


def to_json_object(
    value: Union[_JSON_Primatives, BaseModel],
) -> Union[_JSON_Primatives, Dict[str, Any]]:
    """
    Converts a value to JSON object form.

    Args:
        value: the value to convert

    Returns:
        A JSON-safe representation of the currency amount.
    """
    if isinstance(value, BaseModel):
        return value.to_json_object()
    return value
