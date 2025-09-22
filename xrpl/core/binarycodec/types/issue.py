"""Codec for serializing and deserializing issued currency fields."""

from __future__ import annotations

from typing import Any, Dict, Optional, Type, Union

from typing_extensions import Self

from xrpl.core.binarycodec.binary_wrappers.binary_parser import BinaryParser
from xrpl.core.binarycodec.exceptions import XRPLBinaryCodecException
from xrpl.core.binarycodec.types.account_id import AccountID
from xrpl.core.binarycodec.types.currency import Currency
from xrpl.core.binarycodec.types.hash192 import Hash192
from xrpl.core.binarycodec.types.serialized_type import SerializedType
from xrpl.core.binarycodec.types.uint32 import UInt32
from xrpl.models.currencies import XRP as XRPModel
from xrpl.models.currencies import IssuedCurrency as IssuedCurrencyModel
from xrpl.models.currencies import MPTCurrency as MPTCurrencyModel


class Issue(SerializedType):
    """Codec for serializing and deserializing issued currency fields."""

    BLACK_HOLED_ACCOUNT_ID = AccountID.from_value(
        "0000000000000000000000000000000000000001"
    )

    def __init__(self: Self, buffer: bytes) -> None:
        """
        Construct an Issue from given bytes.

        Args:
            buffer: The byte buffer that will be used to store the serialized
                encoding of this field.
        """
        super().__init__(buffer)

    @classmethod
    def from_value(cls: Type[Self], value: Dict[str, str]) -> Self:
        """
        Construct an Issue object from a string or dictionary representation
        of an issued currency.

        Args:
            value: The dictionary to construct an Issue object from.

        Returns:
            An Issue object constructed from value.

        Raises:
            XRPLBinaryCodecException: If the Issue representation is invalid.
        """
        if XRPModel.is_dict_of_model(value):
            currency_bytes = bytes(Currency.from_value(value["currency"]))
            return cls(currency_bytes)

        if IssuedCurrencyModel.is_dict_of_model(value):
            currency_bytes = bytes(Currency.from_value(value["currency"]))
            issuer_bytes = bytes(AccountID.from_value(value["issuer"]))
            return cls(currency_bytes + issuer_bytes)

        # MPT is serialized as:
        # - 160 bits MPT issuer account (20 bytes)
        # - 160 bits black hole account (20 bytes)
        # - 32 bits sequence (4 bytes)
        # Please look at STIssue.cpp inside rippled implementation for more details.

        if MPTCurrencyModel.is_dict_of_model(value):
            if len(value["mpt_issuance_id"]) != 48:
                raise XRPLBinaryCodecException(
                    "Invalid mpt_issuance_id length: expected 48 characters, "
                    f"received {len(value['mpt_issuance_id'])} characters."
                )
            mpt_issuance_id_bytes = bytes(Hash192.from_value(value["mpt_issuance_id"]))
            return cls(
                bytes(
                    mpt_issuance_id_bytes[:20]
                    + bytes(cls.BLACK_HOLED_ACCOUNT_ID)
                    + bytes(mpt_issuance_id_bytes[20:])
                )
            )

        raise XRPLBinaryCodecException(
            "Invalid type to construct an Issue: expected XRP, IssuedCurrency or "
            f"MPTCurrency as a str or dict, received {value.__class__.__name__}."
        )

    @classmethod
    def from_parser(
        cls: Type[Self],
        parser: BinaryParser,
        length_hint: Optional[int] = None,
    ) -> Self:
        """
        Construct an Issue object from an existing BinaryParser.

        Args:
            parser: The parser to construct the Issue object from.
            length_hint: The number of bytes to consume from the parser.
                For an MPT amount, pass 24 (the fixed length for Hash192).

        Returns:
            The Issue object constructed from a parser.
        """
        currency_or_account = Currency.from_parser(parser)
        if currency_or_account.to_json() == "XRP":
            return cls(bytes(currency_or_account))

        # check if this is an instance of MPTIssuanceID
        issuer_account_id = AccountID.from_parser(parser)
        if issuer_account_id.to_json() == cls.BLACK_HOLED_ACCOUNT_ID.to_json():
            sequence = UInt32.from_parser(parser)
            return cls(
                bytes(currency_or_account)
                + bytes(cls.BLACK_HOLED_ACCOUNT_ID)
                + bytes(sequence)
            )

        return cls(bytes(currency_or_account) + bytes(issuer_account_id))

    def to_json(self: Self) -> Union[str, Dict[Any, Any]]:
        """
        Returns the JSON representation of an issued currency.

        Returns:
            The JSON representation of an Issue.
        """
        # If the buffer's length is 44 bytes (issuer-account + black-hole-account-id +
        # sequence), treat it as a MPTCurrency.
        # Note: hexadecimal representation of the buffer's length is doubled because 1
        # byte is represented by 2 characters in hex.
        if len(self.buffer) == 20 + 20 + 4:
            serialized_mpt_in_hex = self.to_hex().upper()
            return {
                "mpt_issuance_id": serialized_mpt_in_hex[:40]
                + serialized_mpt_in_hex[80:]
            }

        parser = BinaryParser(self.to_hex())
        currency: Union[str, Dict[Any, Any]] = Currency.from_parser(parser).to_json()
        if currency == "XRP":
            return {"currency": currency}

        issuer = AccountID.from_parser(parser)
        return {"currency": currency, "issuer": issuer.to_json()}
