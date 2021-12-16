"""Helper util functions for the models module."""

from dataclasses import is_dataclass
from typing import Any, Dict, List, Type, TypeVar

from xrpl.models.exceptions import XRPLModelException

# Code source for requiring kwargs:
# https://gist.github.com/mikeholler/4be180627d3f8fceb55704b729464adb

_T = TypeVar("_T")
_Self = TypeVar("_Self")


def require_kwargs_on_init(cls: Type[_T]) -> Type[_T]:
    """
    Force a dataclass's init function to only work if called with keyword arguments.
    If parameters are not positional-only, a TypeError is thrown with a helpful message.
    This function may only be used on dataclasses.

    This works by wrapping the __init__ function and dynamically replacing it.
    Therefore, stacktraces for calls to the new __init__ might look a bit strange. Fear
    not though, all is well.

    Note: although this may be used as a decorator, this is not advised as IDEs will no
    longer suggest parameters in the constructor. Instead, this is the recommended
    usage:
        from dataclasses import dataclass
        @dataclass
        class Foo:
            bar: str
        require_kwargs_on_init(Foo)

    Args:
        cls: The class that requires keyword arguments (must be a dataclass).

    Returns:
        The provided class, adding an error on init if positional args are provided.

    Raises:
        TypeError: If cls is None or is not a dataclass.
    """
    # error messages for dev help
    if cls is None:
        raise TypeError("Cannot call with cls=None")
    if not is_dataclass(cls):
        raise TypeError(
            f"This decorator only works on dataclasses. {cls.__name__} is not a "
            "dataclass."
        )

    original_init = cls.__init__

    def new_init(self: _Self, *args: List[Any], **kwargs: Dict[str, Any]) -> None:
        if len(args) > 0:
            raise XRPLModelException(
                f"{type(self).__name__}.__init__ only allows keyword arguments. "
                f"Found the following positional arguments: {args}"
            )
        original_init(self, **kwargs)

    # noinspection PyTypeHints
    cls.__init__ = new_init  # type: ignore

    return cls
