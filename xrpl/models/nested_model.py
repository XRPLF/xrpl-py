"""The base class for models that involve a nested dictionary e.g. memos."""

from __future__ import annotations

from typing import Any, ClassVar, Dict, Type

from xrpl.models.base_model import BaseModel


class NestedModel(BaseModel):
    """The base class for models that involve a nested dictionary e.g. memos."""

    nested_name: ClassVar[str]

    @classmethod
    def is_dict_of_model(cls: Type[NestedModel], dictionary: Any) -> bool:
        """
        Returns True if the input dictionary was derived by the `to_dict`
        method of an instance of this class. In other words, True if this is
        a dictionary representation of an instance of this class.

        NOTE: does not account for model inheritance, IE will only return True
        if dictionary represents an instance of this class, but not if
        dictionary represents an instance of a subclass of this class.

        Args:
            dictionary: The dictionary to check.

        Returns:
            True if dictionary is a dict representation of an instance of this
            class.
        """
        return (
            isinstance(dictionary, dict)
            and cls.nested_name in dictionary
            and super().is_dict_of_model(dictionary[cls.nested_name])
        )

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
