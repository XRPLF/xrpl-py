"""The base class for all model types."""

from __future__ import annotations

import json
import re
from abc import ABC
from dataclasses import fields
from enum import Enum
from typing import Any, Dict, List, Pattern, Type, Union, cast, get_type_hints

from typing_extensions import Final, get_args, get_origin

from xrpl.models.exceptions import XRPLModelException
from xrpl.models.required import REQUIRED
from xrpl.models.types import XRPL_VALUE_TYPE

# this regex splits words based on one of three cases:
#
# 1. 1-or-more non-capital chars at the beginning of the string. Handles cases
# like "value" where the entire string is not capitalized. Would also handle
# true camelCase instead of PascalCase
_CAMEL_CASE_LEADING_LOWER: Final[str] = "^[^A-Z]+"
# 2. 1-or-more capital chars NOT followed by a non-capital char. Handles
# abbreviated PascalCase values like "URI".
_CAMEL_CASE_ABBREVIATION: Final[str] = "[A-Z]+(?![^A-Z])"
# 3. 1 capital char followed by N non-capital-chars. Handles the typical
# PascalCase like "Amount"
_CAMEL_CASE_TYPICAL: Final[str] = "[A-Z][^A-Z]*"
#
# combining the above together into one regex:
_CAMEL_TO_SNAKE_CASE_REGEX: Final[Pattern[str]] = re.compile(
    f"(?:{_CAMEL_CASE_LEADING_LOWER}|{_CAMEL_CASE_ABBREVIATION}|{_CAMEL_CASE_TYPICAL})"
)
# used for converting special substrings inside CamelCase fields
SPECIAL_CAMELCASE_STRINGS = ["NFToken"]


def _key_to_json(field: str) -> str:
    """
    Transforms camelCase or PascalCase to snake_case. For example:
        1. 'TransactionType' becomes 'transaction_type'
        2. 'value' remains 'value'
        3. 'URI' becomes 'uri'
    """
    # convert all special CamelCase substrings to capitalized strings
    for spec_str in SPECIAL_CAMELCASE_STRINGS:
        if spec_str in field:
            field = field.replace(spec_str, spec_str.capitalize())

    return "_".join(
        [word.lower() for word in _CAMEL_TO_SNAKE_CASE_REGEX.findall(field)]
    )


def _value_to_json(value: XRPL_VALUE_TYPE) -> XRPL_VALUE_TYPE:
    if isinstance(value, dict):
        return {_key_to_json(k): _value_to_json(v) for (k, v) in value.items()}
    if isinstance(value, list):
        return [_value_to_json(sub_value) for sub_value in value]
    return value


class BaseModel(ABC):
    """The base class for all model types."""

    @classmethod
    def is_dict_of_model(cls: Type[BaseModel], dictionary: Any) -> bool:
        """
        Checks whether the provided ``dictionary`` is a dictionary representation
        of this class.

        **Note:** This only checks the exact model, and does not count model
        inheritance. This method returns ``False`` if the dictionary represents
        a subclass of this class.

        Args:
            dictionary: The dictionary to check.

        Returns:
            True if dictionary is a ``dict`` representation of an instance of this
            class; False if not.
        """
        return (
            isinstance(dictionary, dict)
            and set(get_type_hints(cls).keys()).issuperset(set(dictionary.keys()))
            and all(
                [
                    attr in dictionary
                    for attr, value in get_type_hints(cls).items()
                    if value is REQUIRED
                ]
            )
        )

    @classmethod
    def from_dict(cls: Type[BaseModel], value: Dict[str, XRPL_VALUE_TYPE]) -> BaseModel:
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

            args[param] = cls._from_dict_single_param(
                param, class_types[param], value[param]
            )

        init = cls._get_only_init_args(args)
        return cls(**init)

    @classmethod
    def _from_dict_single_param(
        cls: Type[BaseModel],
        param: str,
        param_type: Type[Any],
        param_value: Union[int, str, bool, BaseModel, Enum, List[Any], Dict[str, Any]],
    ) -> Any:
        """Recursively handles each individual param in `from_dict`."""
        param_type_origin = get_origin(param_type)
        # returns `list` if a List, `Union` if a Union, None otherwise

        if param_type_origin is list and isinstance(param_value, list):
            # expected a List, received a List
            list_type = get_args(param_type)[0]
            return [
                cls._from_dict_single_param(param, list_type, item)
                for item in param_value
            ]

        if param_type_origin is Union:
            for param_type_option in get_args(param_type):
                # iterate through the types Union-ed together
                try:
                    # try to use this Union-ed type to process param_value
                    return cls._from_dict_single_param(
                        param, param_type_option, param_value
                    )
                except XRPLModelException:
                    # this Union-ed type did not work, move onto the next one
                    pass

        # no more collections (no params expect a Dict)

        if param_type is Any:
            # param_type is Any (e.g. will accept anything)
            return param_value

        if isinstance(param_type, type) and isinstance(param_value, param_type):
            # expected an object, received the correct object
            return param_value

        if (
            isinstance(param_type, type)
            and issubclass(param_type, Enum)
            and param_value in list(param_type)
        ):
            # expected an Enum and received a valid value for it.
            # for some reason required for string enums.
            return param_value

        if (
            isinstance(param_type, type)
            and issubclass(param_type, BaseModel)
            and isinstance(param_value, dict)
        ):
            # expected an XRPL Model, received a Dict
            return cast(BaseModel, param_type).from_dict(param_value)

        # received something we didn't expect, raise an error
        if isinstance(param_type, type) and issubclass(param_type, BaseModel):
            error_message = (
                f"{param} expected a {param_type} or a Dict representing {param_type}, "
                f"received a {type(param_value)}"
            )
        else:
            error_message = (
                f"{param} expected a {param_type}, received a {type(param_value)}"
            )
        raise XRPLModelException(error_message)

    @classmethod
    def _get_only_init_args(
        cls: Type[BaseModel], args: Dict[str, Any]
    ) -> Dict[str, Any]:
        init_keys = {field.name for field in fields(cls) if field.init is True}
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
            for (k, v) in cast(Dict[str, XRPL_VALUE_TYPE], value).items()
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
        # mypy doesn't realize that BaseModel has a field called __dataclass_fields__
        dataclass_fields = self.__dataclass_fields__.keys()  # type: ignore
        return {
            key: self._to_dict_elem(getattr(self, key))
            for key in dataclass_fields
            if getattr(self, key) is not None
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
