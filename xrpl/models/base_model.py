"""TODO: docstring"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Dict


class BaseModel(ABC):
    """TODO: docstring"""

    @classmethod
    @abstractmethod
    def from_dict(cls: BaseModel, value: Dict[str, Any]) -> BaseModel:
        """
        Construct a new BaseModel from a literal value.

        Args:
            value: The value to construct the BaseModel from.

        Raises:
            NotImplementedError: Always.
        """
        raise NotImplementedError("BaseModel.from_value not implemented.")

    @abstractmethod
    def to_json(self: BaseModel) -> Dict[str, Any]:
        """TODO: docstring"""
        raise NotImplementedError("BaseModel.to_json not implemented.")
