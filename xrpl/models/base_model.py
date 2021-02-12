"""The base class for all model types."""

from __future__ import annotations

from abc import ABC
from typing import Any, Dict

from xrpl.models.exceptions import XRPLModelValidationException


class BaseModel(ABC):
    """The base class for all model types."""

    @classmethod
    def from_dict(cls: BaseModel, value: Dict[str, Any]) -> BaseModel:
        """
        Construct a new BaseModel from a dictionary of parameters.

        If not overridden, passes the dictionary as args to the constructor.

        Args:
            value: The value to construct the BaseModel from.

        Returns:
            A new BaseModel object, constructed using the given parameters.
        """
        cls.validate(value)
        return cls(**value)

    @classmethod
    def validate(self: BaseModel, value: Dict[str, Any]) -> None:
        """
        Raises an error if the arguments provided are invalid for a BaseModel object.

        Args:
            value: The value to construct the BaseModel from.

        Raises:
            XRPLModelValidationException: if the arguments provided are invalid for the
                creation of a BaseModel object.
        """
        validation_errors = self._get_validation_errors(value)
        if len(validation_errors) > 0:
            raise XRPLModelValidationException(str(validation_errors))

    @classmethod
    def is_valid(cls: BaseModel, value: Dict[str, Any]) -> bool:
        """
        Returns whether the dictionary provided contains valid arguments.

        Args:
            value: The value to construct the BaseModel from.

        Returns:
            Whether the dictionary provided contains valid arguments.
        """
        return len(cls._get_validation_errors(value))

    @classmethod
    def _get_validation_errors(cls: BaseModel, value: Dict[str, Any]) -> Dict[str, str]:
        return {}

    def to_json_object(self: BaseModel) -> Dict[str, Any]:
        """
        Returns the JSON representation of a BaseModel.

        If not overridden, returns the object dict with all non-None values.

        Returns:
            The JSON representation of a BaseModel.
        """
        return {
            key: value for (key, value) in self.__dict__.items() if value is not None
        }

    def __eq__(self: BaseModel, other: object) -> bool:
        """Compares a BaseModel to another object to determine if they are equal."""
        if not isinstance(other, BaseModel):
            return False
        return self.to_json_object() == other.to_json_object()

    def __repr__(self: BaseModel) -> str:
        """Returns a string representation of a BaseModel object"""
        repr_items = []
        for key, value in self.to_json_object().items():
            repr_items.append(f"{key}={repr(value)}")
        return "{}({})".format(type(self).__name__, ", ".join(repr_items))
