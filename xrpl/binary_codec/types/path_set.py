"""Classes and methods related to serializing and deserializing PathSets."""

from __future__ import annotations

from typing import Dict, List

from xrpl.binary_codec.binary_wrappers.binary_parser import BinaryParser
from xrpl.binary_codec.exceptions import XRPLBinaryCodecException
from xrpl.binary_codec.types.account_id import AccountID
from xrpl.binary_codec.types.currency import Currency
from xrpl.binary_codec.types.serialized_type import SerializedType

# Constant for masking types of a PathStep
TYPE_ACCOUNT = 0x01
TYPE_CURRENCY = 0x10
TYPE_ISSUER = 0x20

# Constants for separating Paths in a PathSet
PATHSET_END_BYTE = 0x00
PATH_SEPARATOR_BYTE = 0xFF


def _is_path_step(value: Dict[str, str]):
    return "issuer" in value or "account" in value or "currency" in value


def _is_path_set(value: List[List[Dict[str, str]]]):
    return len(value) == 0 or len(value[0]) == 0 or _is_path_step(value[0][0])


class PathStep(SerializedType):
    """Serialize and deserialize a single step in a Path."""

    @classmethod
    def from_value(cls, value: Dict[str, str]) -> PathStep:
        """Create a PathStep from a dictionary."""
        data_type = 0x00
        buffer = b""
        if "account" in value:
            account_id = AccountID.from_value(value["account"])
            buffer += account_id.to_bytes()
            data_type |= TYPE_ACCOUNT
        if "currency" in value:
            currency = Currency.from_value(value["currency"])
            buffer += currency.to_bytes()
            data_type |= TYPE_CURRENCY
        if "issuer" in value:
            issuer = AccountID.from_value(value["issuer"])
            buffer += issuer.to_bytes()
            data_type |= TYPE_ISSUER

        return PathStep(bytes([data_type]) + buffer)

    @classmethod
    def from_parser(cls, parser: BinaryParser) -> PathStep:
        """Construct a PathStep from a BinaryParser."""
        data_type = parser.read_uint8()
        buffer = b""

        if data_type & TYPE_ACCOUNT:
            account_id = parser.read(AccountID.LENGTH)
            buffer += account_id
        if data_type & TYPE_CURRENCY:
            currency = parser.read(Currency.LENGTH)
            buffer += currency
        if data_type & TYPE_ISSUER:
            issuer = parser.read(AccountID.LENGTH)
            buffer += issuer

        return PathStep(bytes([data_type]) + buffer)

    def to_json(self) -> Dict[str, str]:
        """Get the JSON interpretation of this PathStep."""
        parser = BinaryParser(self.to_string())
        data_type = parser.read_uint8()
        json = {}

        if data_type & TYPE_ACCOUNT:
            account_id = AccountID.from_parser(parser).to_json()
            json["account"] = account_id
        if data_type & TYPE_CURRENCY:
            currency = Currency.from_parser(parser).to_json()
            json["currency"] = currency
        if data_type & TYPE_ISSUER:
            issuer = AccountID.from_parser(parser).to_json()
            json["issuer"] = issuer

        return json

    @property
    def type(self) -> int:
        """Get a number representing the type of this PathStep.

        Returns:
            a number to be bitwise and-ed with TYPE_ constants to describe the types in
            the PathStep.
        """
        return self.buffer[0]


class Path(SerializedType):
    """Class for serializing/deserializing Paths."""

    @classmethod
    def from_value(cls, value: List[Dict[str, str]]) -> Path:
        """Construct a Path from an array of dictionaries describing PathSteps."""
        buffer: bytes = b""
        for PathStep_dict in value:
            pathstep = PathStep.from_value(PathStep_dict)
            buffer += pathstep.to_bytes()
        return Path(buffer)

    @classmethod
    def from_parser(cls, parser: BinaryParser) -> Path:
        """Construct a Path from a BinaryParser."""
        buffer: List[bytes] = []
        while not parser.is_end():
            pathstep = PathStep.from_parser(parser)
            buffer.append(pathstep.to_bytes())

            if (
                parser.peek() == PATHSET_END_BYTE
                or parser.peek() == PATH_SEPARATOR_BYTE
            ):
                break
        return Path(b"".join(buffer))

    def to_json(self) -> List[Dict[str, str]]:
        """Get the JSON representation of this Path."""
        json = []
        path_parser = BinaryParser(self.to_string())

        while not path_parser.is_end():
            pathstep = PathStep.from_parser(path_parser)
            json.append(pathstep.to_json())

        return json


class PathSet(SerializedType):
    """Deserialize and Serialize the PathSet type."""

    @classmethod
    def from_value(cls, value: List[List[Dict[str, str]]]) -> PathSet:
        """Construct a PathSet from a List of Lists representing paths."""
        if _is_path_set(value):
            buffer: List[bytes] = []
            for path_dict in value:
                path = Path.from_value(path_dict)
                buffer.append(path.to_bytes())
                buffer.append(bytes([PATH_SEPARATOR_BYTE]))

            buffer[-1] = bytes([PATHSET_END_BYTE])
            return PathSet(b"".join(buffer))

        raise XRPLBinaryCodecException("Cannot construct PathSet from given value")

    @classmethod
    def from_parser(cls, parser: BinaryParser) -> PathSet:
        """Construct a PathSet from a BinaryParser."""
        buffer: List[bytes] = []
        while not parser.is_end():
            path = Path.from_parser(parser)
            buffer.append(path.to_bytes())
            buffer.append(parser.read(1))

            if buffer[-1][0] == PATHSET_END_BYTE:
                break
        return PathSet(b"".join(buffer))

    def to_json(self) -> List[List[Dict[str, str]]]:
        """Get the JSON representation of this PathSet."""
        json = []
        pathset_parser = BinaryParser(self.to_string())

        while not pathset_parser.is_end():
            path = Path.from_parser(pathset_parser)
            json.append(path.to_json())
            pathset_parser.skip(1)

        return json
