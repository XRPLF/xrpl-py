"""The base class for all model types."""

from __future__ import annotations

from abc import ABC
from dataclasses import fields
from enum import Enum
from typing import Any, Dict, Type, Union, get_type_hints

from xrpl.models.exceptions import XRPLModelException
from xrpl.models.required import REQUIRED


class BaseModel(ABC):
    """The base class for all model types."""

    @classmethod
    def from_dict(cls: Type[BaseModel], value: Dict[str, Any]) -> BaseModel:
        """
        Construct a new BaseModel from a dictionary of parameters.

        If not overridden, passes the dictionary as args to the constructor.

        Args:
            value: The value to construct the BaseModel from.

        Returns:
            A new BaseModel object, constructed using the given parameters.

        Raises:
            XRPLModelException: If the dictionary provided is invalid.
        """
        # returns a dictionary mapping class params to their types
        class_types = get_type_hints(cls)

        args = {}
        for param in value:
            if param not in class_types:
                raise XRPLModelException(
                    f"{param} not a valid parameter for {cls.__name__}"
                )
            if type(value[param]) == class_types[param]:
                # the type of the param provided matches the type expected for the param
                args[param] = value[param]
            else:
                args[param] = cls._from_dict_special_cases(
                    param, class_types[param], value[param]
                )

        init = cls._get_only_init_args(args)
        # Ignore type-checking on this for now to simplify subclass constructors
        # which might pass non kwargs.
        return cls(**init)  # type: ignore

    @classmethod
    def _from_dict_special_cases(
        cls: Type[BaseModel],
        param: str,
        param_type: Type[Any],
        param_value: Dict[str, Any],
    ) -> Union[Enum, BaseModel, Dict[str, Any]]:
        """Handles all the recursive/more complex cases for `from_dict`."""
        from xrpl.models.amounts import Amount, IssuedCurrencyAmount
        from xrpl.models.currencies import XRP, Currency, IssuedCurrency
        from xrpl.models.transactions.transaction import Transaction

        # TODO: figure out how to make NewTypes work generically (if possible)

        if param_type == Amount:
            # special case, NewType
            if not isinstance(param_value, dict):
                raise XRPLModelException(
                    f"{param_type} requires a dictionary of params"
                )
            return IssuedCurrencyAmount.from_dict(param_value)

        if param_type == Currency:
            # special case, NewType
            if not isinstance(param_value, dict):
                raise XRPLModelException(
                    f"{param_type} requires a dictionary of params"
                )
            if "currency" in param_value and "issuer" in param_value:
                return IssuedCurrency.from_dict(param_value)
            if "currency" in param_value:
                return XRP.from_dict(param_value)
            raise XRPLModelException(f"No valid type for {param}")

        if param_type == Transaction:
            # special case, multiple options (could be any Transaction type)
            if "transaction_type" not in param_value:
                raise XRPLModelException(
                    f"{param} not a valid parameter for {cls.__name__}"
                )
            type_str = param_value["transaction_type"]
            # safely convert type string into the actual type
            transaction_type = Transaction.get_transaction_type(type_str)
            return transaction_type.from_dict(param_value)

        if param_type in BaseModel.__subclasses__():
            # any other BaseModel
            if not isinstance(param_value, dict):
                raise XRPLModelException(
                    f"{param_type} requires a dictionary of params"
                )
            # mypy doesn't know that the If checks that it's a subclass of BaseModel
            return param_type.from_dict(param_value)  # type: ignore

        if param_type in Enum.__subclasses__():
            # mypy doesn't know that the If checks that it's a subclass of Enum
            return param_type(param_value)  # type: ignore

        return param_value

    @classmethod
    def _get_only_init_args(
        cls: Type[BaseModel], args: Dict[str, Any]
    ) -> Dict[str, Any]:
        init_keys = {field.name for field in fields(cls)}
        valid_args = {key: value for key, value in args.items() if key in init_keys}
        return valid_args

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
