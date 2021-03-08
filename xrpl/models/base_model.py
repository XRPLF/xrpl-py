"""The base class for all model types."""

from __future__ import annotations

from abc import ABC
from typing import Any, Dict, get_type_hints

from xrpl.models.exceptions import XRPLModelValidationException
from xrpl.models.required import REQUIRED


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
        from xrpl.models.amounts import Amount, IssuedCurrencyAmount
        from xrpl.models.currencies import XRP, Currency, IssuedCurrency

        class_types = get_type_hints(cls)
        args = {}
        for param in value:
            if param not in class_types:
                raise XRPLModelValidationException(
                    f"{param} not a valid parameter for {cls.__name__}"
                )
            if type(value[param]) == class_types[param]:
                args[param] = value[param]
            else:
                param_type = class_types[param]
                # TODO: figure out how to make NewTypes work generically (if possible)
                if param_type == Amount:  # special case, NewType
                    if isinstance(value[param], dict):
                        new_obj = IssuedCurrencyAmount.from_dict(value[param])
                        args[param] = new_obj
                elif param_type == Currency:
                    if isinstance(value[param], dict):
                        if "currency" in value[param] and "issuer" in value[param]:
                            new_obj = IssuedCurrency.from_dict(value[param])
                        elif "currency" in value[param]:
                            new_obj = XRP.from_dict(value[param])
                        else:
                            raise XRPLModelValidationException(
                                f"No valid type for {param}"
                            )
                        args[param] = new_obj
                    if isinstance(value[param], str):
                        new_obj = XRP(currency=value[param])
                        args[param] = new_obj
        return cls(**args)

    def __post_init__(self: BaseModel) -> None:
        """Called by dataclasses immediately after __init__."""
        self.validate()

    def validate(self: BaseModel) -> None:
        """
        Raises if this object is invalid.

        Raises:
            XRPLModelValidationException: if this object is invalid.
        """
        errors = self._get_errors()
        if len(errors) > 0:
            raise XRPLModelValidationException(str(errors))

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
        return {
            key: value.to_dict() if isinstance(value, BaseModel) else value
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
