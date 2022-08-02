"""The base class for models that involve a nested dictionary e.g. memos."""

from __future__ import annotations

from typing import Any, ClassVar, Dict, Type

from xrpl.models.base_model import BaseModel


class NestedModel(BaseModel):
    """The base class for models that involve a nested dictionary e.g. memos."""

    nested_name: ClassVar[str]

    @classmethod
    def from_dict(cls: Type[NestedModel], value: Dict[str, Any]) -> NestedModel:
        """
        Construct a new NestedModel from a dictionary of parameters.

        Args:
            value: The value to construct the NestedModel from.

        Returns:
            A new NestedModel object, constructed using the given parameters.

        Raises:
            XRPLModelException: If the dictionary provided is invalid.
        """
        if cls.nested_name not in value:
            return super(NestedModel, cls).from_dict(value)
        return super(NestedModel, cls).from_dict(value[cls.nested_name])

    def to_dict(self: NestedModel) -> Dict[str, Any]:
        """
        Returns the dictionary representation of a NestedModel.

        Returns:
            The dictionary representation of a NestedModel.
        """
        return {self.nested_name: super().to_dict()}
