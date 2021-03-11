"""The base class for all model types."""

from __future__ import annotations

from abc import ABC
from typing import Any, Dict, Type

from typing_extensions import Final

from xrpl.models.exceptions import XRPLModelException

# A sentinel object used to determine if a given field is not set. Using this
# allows us to not worry about argument ordering and treat all arguments to
# __init__ as kwargs.
REQUIRED: Final[object] = object()


class BaseModel(ABC):
    """The base class for all model types."""

    def __init__(self: BaseModel, **kwargs: str) -> BaseModel:
        """Constructs a new BaseModel from a set of keyword arguments."""
        self.__dict__.update(kwargs)

    @classmethod
    def from_dict(cls: Type[BaseModel], value: Dict[str, Any]) -> BaseModel:
        """
        Construct a new BaseModel from a dictionary of parameters.

        If not overridden, passes the dictionary as args to the constructor.

        Args:
            value: The value to construct the BaseModel from.

        Returns:
            A new BaseModel object, constructed using the given parameters.
        """
        return cls(**value)

    def __post_init__(self: BaseModel) -> None:
        """Called by dataclasses immediately after __init__."""
        self.validate()

    def validate(self: BaseModel) -> None:
        """
        Raises if this object is invalid.

        Raises:
            XRPLModelException: if this object is invalid.
        """
        errors = self._get_errors()
        if len(errors) > 0:
            raise XRPLModelException(str(errors))

    def is_valid(self: BaseModel) -> bool:
        """
        Returns whether this BaseModel is valid.

        Returns:
            Whether this BaseModel is valid.
        """
        return len(self._get_errors()) == 0

    def _get_errors(self: BaseModel) -> Dict[str, str]:
        """
        Extended in subclasses to define custom validation logic.

        Returns:
            Dictionary of any errors found on self.
        """
        return {
            attr: f"{attr} is not set"
            for attr, value in self.__dict__.items()
            if value is REQUIRED
        }

    def to_dict(self: BaseModel) -> Dict[str, Any]:
        """
        Returns the dictionary representation of a BaseModel.

        If not overridden, returns the object dict with all non-None values.

        Returns:
            The dictionary representation of a BaseModel.
        """

        def _format_elem(elem: Any) -> Any:
            if isinstance(elem, BaseModel):
                return elem.to_dict()
            if isinstance(elem, list):
                return [
                    _format_elem(sub_elem) for sub_elem in elem if sub_elem is not None
                ]
            return elem

        return {
            key: _format_elem(value)
            for key, value in self.__dict__.items()
            if value is not None
        }

    def __eq__(self: BaseModel, other: object) -> bool:
        """Compares a BaseModel to another object to determine if they are equal."""
        if not isinstance(other, BaseModel):
            return False
        return self.to_dict() == other.to_dict()

    def __repr__(self: BaseModel) -> str:
        """Returns a string representation of a BaseModel object"""
        repr_items = [f"{key}={repr(value)}" for key, value in self.to_dict().items()]
        return f"{type(self).__name__}({repr_items})"
