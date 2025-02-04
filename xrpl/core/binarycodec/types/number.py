from typing import TYPE_CHECKING, Any, Dict, Optional, Type

from typing_extensions import Self

from xrpl.core.binarycodec.binary_wrappers.binary_parser import BinaryParser
from xrpl.core.binarycodec.types.serialized_type import SerializedType


class Number(SerializedType):
    """Codec for serializing and deserializing Number fields."""

    def __init__(self: Self, buffer: bytes) -> None:
        """Construct a Number from given bytes."""
        super().__init__(buffer)

    @classmethod
    def from_parser(  # noqa: D102
        cls: Type[Self],
        parser: BinaryParser,
        # length_hint is Any so that subclasses can choose whether or not to require it.
        length_hint: Any,  # noqa: ANN401
    ) -> Self:
        pass

    @classmethod
    def from_value(cls: Type[Self], value: Dict[str, Any]) -> Self:
        return cls(bytes(value))

    # def to_json(self: Self) -> Dict[str, Any]:
    #     pass
