"""The base class for all model types."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Dict


class BaseModel(ABC):
    """The base class for all model types."""

    @classmethod
    @abstractmethod
    def from_dict(cls: BaseModel, value: Dict[str, Any]) -> BaseModel:
        """
        Construct a new BaseModel from a dictionary of parameters.

        Args:
            value: The value to construct the BaseModel from.

        Raises:
            NotImplementedError: Always.
        """
        raise NotImplementedError("BaseModel.from_value not implemented.")

    def to_json(self: BaseModel) -> Dict[str, Any]:
        """
        Returns the JSON representation of a BaseModel.

        If not overridden, returns the object dict.
        """
        return {
            key: value for (key, value) in self.__dict__.items() if value is not None
        }

    def __eq__(self: BaseModel, other: object) -> bool:
        """Compares a BaseModel to another object to determine if they are equal."""
        if not isinstance(other, BaseModel):
            return False
        return self.to_json() == other.to_json()

    def __repr__(self: BaseModel) -> str:
        """Returns a string representation of a BaseModel object"""
        repr_items = []
        for key, value in self.to_json().items():
            repr_items.append(f"{key}={repr(value)}")
        return "{}({})".format(type(self).__name__, ", ".join(repr_items))
