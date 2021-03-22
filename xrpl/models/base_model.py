"""The base class for all model types."""

from __future__ import annotations

import json
from abc import ABC
from dataclasses import fields
from enum import Enum
from re import split, sub
from typing import Any, Dict, Type, Union, cast, get_type_hints

from xrpl.models.exceptions import XRPLModelException
from xrpl.models.required import REQUIRED


def _key_to_json(field: str) -> str:
    """
    Transforms (upper or lower) camel case to snake case. For example, 'TransactionType'
    becomes 'transaction_type'.
    """
    words = split(r"(?=[A-Z])", field)
    lower_words = [word.lower() for word in words if word]
    snaked = "_".join(lower_words)
    return sub("i_d", "id", snaked)


def _value_to_json(value: str) -> str:
    if isinstance(value, dict):
        return {
            _key_to_json(k): _value_to_json(v)
            for (k, v) in cast(Dict[str, Any], value).items()
        }
    if isinstance(value, list):
        return [_value_to_json(sub_value) for sub_value in value]
    return value


class BaseModel(ABC):
    """The base class for all model types."""

    @classmethod
    def from_dict(cls: Type[BaseModel], value: Dict[str, Any]) -> BaseModel:
        """
        Construct a new BaseModel from a dictionary of parameters.

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
    ) -> Union[str, Enum, BaseModel, Dict[str, Any]]:
        """Handles all the recursive/more complex cases for `from_dict`."""
        from xrpl.models.amounts import Amount, IssuedCurrencyAmount
        from xrpl.models.currencies import XRP, Currency, IssuedCurrency
        from xrpl.models.transactions.transaction import Transaction

        # TODO: figure out how to make Unions work generically (if possible)

        if param_type == Amount:
            # special case, Union
            if isinstance(param_value, str):
                return param_value
            if not isinstance(param_value, dict):
                raise XRPLModelException(
                    f"{param_type} requires a dictionary of params"
                )
            return IssuedCurrencyAmount.from_dict(param_value)

        if param_type == Currency:
            # special case, Union
            if not isinstance(param_value, dict):
                raise XRPLModelException(
                    f"{param_type} requires a dictionary of params"
                )
            if "currency" in param_value and "issuer" in param_value:
                return IssuedCurrency.from_dict(param_value)
            if "currency" in param_value:
                param_value_copy = {**param_value}
                del param_value_copy["currency"]
                return XRP.from_dict(param_value_copy)
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
            param_value_copy = {**param_value}
            del param_value_copy["transaction_type"]
            return transaction_type.from_dict(param_value_copy)

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

    @classmethod
    def from_xrpl(cls: Type[BaseModel], value: Union[str, Dict[str, Any]]) -> BaseModel:
        """
        Creates a BaseModel object based on a JSON-like dictionary of keys in the JSON
        format used by the binary codec, or an actual JSON string representing the same
        data.

        Args:
            value: The dictionary or JSON string to be instantiated.

        Returns:
            A BaseModel object instantiated from the input.
        """
        if isinstance(value, str):
            value = json.loads(value)

        formatted_dict = {
            _key_to_json(k): _value_to_json(v)
            for (k, v) in cast(Dict[str, Any], value).items()
        }

        return cls.from_dict(formatted_dict)

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
        return {
            key: self._to_dict_elem(value)
            for key, value in self.__dict__.items()
            if value is not None
        }

    def _to_dict_elem(self: BaseModel, elem: Any) -> Any:
        if isinstance(elem, BaseModel):
            return elem.to_dict()
        if isinstance(elem, Enum):
            return elem.value
        if isinstance(elem, list):
            return [
                self._to_dict_elem(sub_elem)
                for sub_elem in elem
                if sub_elem is not None
            ]
        return elem

    def __eq__(self: BaseModel, other: object) -> bool:
        """Compares a BaseModel to another object to determine if they are equal."""
        return isinstance(other, BaseModel) and self.to_dict() == other.to_dict()

    def __repr__(self: BaseModel) -> str:
        """Returns a string representation of a BaseModel object"""
        repr_items = [f"{key}={repr(value)}" for key, value in self.to_dict().items()]
        return f"{type(self).__name__}({repr_items})"
