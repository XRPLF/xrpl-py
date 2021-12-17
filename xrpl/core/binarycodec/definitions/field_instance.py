"""A collection of serialization information about a specific field type."""
from __future__ import annotations  # Requires Python 3.7+

from typing import TYPE_CHECKING, Dict, Type

from xrpl.core.binarycodec.definitions.field_header import FieldHeader
from xrpl.core.binarycodec.definitions.field_info import FieldInfo

if TYPE_CHECKING:
    # To prevent a circular dependency.
    from xrpl.core.binarycodec.types.serialized_type import SerializedType


def _get_type_by_name(name: str) -> Type[SerializedType]:
    """
    Convert the string name of a class to the class object itself.

    Args:
        name: the name of the class.

    Returns:
        The corresponding class object.
    """
    from xrpl.core.binarycodec.types.account_id import AccountID
    from xrpl.core.binarycodec.types.amount import Amount
    from xrpl.core.binarycodec.types.blob import Blob
    from xrpl.core.binarycodec.types.currency import Currency
    from xrpl.core.binarycodec.types.hash128 import Hash128
    from xrpl.core.binarycodec.types.hash160 import Hash160
    from xrpl.core.binarycodec.types.hash256 import Hash256
    from xrpl.core.binarycodec.types.path_set import PathSet
    from xrpl.core.binarycodec.types.serialized_dict import SerializedDict
    from xrpl.core.binarycodec.types.serialized_list import SerializedList
    from xrpl.core.binarycodec.types.uint8 import UInt8
    from xrpl.core.binarycodec.types.uint16 import UInt16
    from xrpl.core.binarycodec.types.uint32 import UInt32
    from xrpl.core.binarycodec.types.uint64 import UInt64
    from xrpl.core.binarycodec.types.vector256 import Vector256

    type_map: Dict[str, Type[SerializedType]] = {
        "AccountID": AccountID,
        "Amount": Amount,
        "Blob": Blob,
        "Currency": Currency,
        "Hash128": Hash128,
        "Hash160": Hash160,
        "Hash256": Hash256,
        "PathSet": PathSet,
        "STArray": SerializedList,
        "STObject": SerializedDict,
        "UInt8": UInt8,
        "UInt16": UInt16,
        "UInt32": UInt32,
        "UInt64": UInt64,
        "Vector256": Vector256,
    }

    return type_map[name]


class FieldInstance:
    """A collection of serialization information about a specific field type."""

    def __init__(
        self: FieldInstance,
        field_info: FieldInfo,
        field_name: str,
        field_header: FieldHeader,
    ) -> None:
        """
        Construct a FieldInstance.

        :param field_info: The field's serialization info from definitions.json.
        :param field_name: The field's string name.
        :param field_header: A FieldHeader object with the type_code and field_code.
        """
        self.nth = field_info.nth
        self.is_variable_length_encoded = field_info.is_variable_length_encoded
        self.is_serialized = field_info.is_serialized
        self.is_signing = field_info.is_signing_field
        self.type = field_info.type
        self.name = field_name
        self.header = field_header
        self.ordinal = self.header.type_code << 16 | self.nth
        self.associated_type = _get_type_by_name(self.type)
