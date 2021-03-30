"""The base class for all model types."""

from __future__ import annotations

import json
from abc import ABC
from dataclasses import fields
from enum import Enum
from re import split, sub
from typing import Any, Dict, List, Type, Union, cast, get_type_hints

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
    def is_dict_of_model(cls: Type[BaseModel], dictionary: Dict[str, Any]) -> bool:
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
        return isinstance(dictionary, dict) and set(get_type_hints(cls).keys()) == set(
            dictionary.keys()
        )

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

            args[param] = cls._from_dict_single_param(
                param, class_types[param], value[param]
            )

        init = cls._get_only_init_args(args)
        # Ignore type-checking on this for now to simplify subclass constructors
        # which might pass non kwargs.
        return cls(**init)  # type: ignore

    @classmethod
    def _from_dict_single_param(
        cls: Type[BaseModel],
        param: str,
        param_type: Type[Any],
        param_value: Dict[str, Any],
    ) -> Any:
        """Recursively handles each individual param in `from_dict`."""
        if type(param_value) == param_type:
            # the type of the param provided matches the type expected for the param
            return param_value

        if "xrpl.models" in param_type.__module__:  # any model defined in xrpl.models
            if not isinstance(param_value, dict):
                raise XRPLModelException(
                    f"{param_type} requires a dictionary of params"
                )
            return cast(BaseModel, param_type).from_dict(param_value)

        if param_type in Enum.__subclasses__():  # an Enum
            return param_type(param_value)

        # param_type must be something from typing - e.g. List, Union, Any
        # there are no models that have Dict params
        if param_type == Any:
            # param_type is Any
            return param_value

        if param_type.__reduce__()[1][0] == List:
            # param_type is a List
            if not isinstance(param_value, List):
                raise XRPLModelException(
                    f"{param} expected a List, received a {type(param_value)}"
                )
            list_type = param_type.__reduce__()[1][1]
            new_list = []
            for item in param_value:
                new_list.append(cls._from_dict_single_param(param, list_type, item))
            return new_list

        if param_type.__reduce__()[1][0] == Union:
            # param_type is a Union
            for param_type_option in param_type.__args__:
                # iterate through the types Union-ed together
                try:
                    # try to use this Union-ed type to process param_value
                    return cls._from_dict_single_param(
                        param, param_type_option, param_value
                    )
                except XRPLModelException:
                    # this Union-ed type did not work
                    # move onto the next one
                    continue

        raise XRPLModelException(
            f"{param} expected a {param_type}, received a {type(param_value)}"
        )

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
