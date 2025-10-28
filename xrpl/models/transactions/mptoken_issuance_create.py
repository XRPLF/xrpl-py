"""Model for MPTokenIssuanceCreate transaction type."""

from __future__ import annotations

import warnings
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, TypedDict, Union

from typing_extensions import Final, Self

from xrpl.models.transactions.transaction import Transaction, TransactionFlagInterface
from xrpl.models.transactions.types import TransactionType
from xrpl.models.utils import (
    HEX_REGEX,
    MAX_MPTOKEN_METADATA_LENGTH,
    MPT_META_WARNING_HEADER,
    require_kwargs_on_init,
    validate_mptoken_metadata,
)

_MAX_TRANSFER_FEE: Final[int] = 50000


class MPTokenMetadataUri(TypedDict, total=False):
    """
    MPTokenMetadataUri object as per the XLS-89 standard.
    Represents a URI entry in the MPTokenMetadata using long-form field names.
    Used within the `uris` array of {@link MPTokenMetadata}.
    """

    uri: str
    """
    URI to the related resource.
    Can be a `hostname/path` (HTTPS assumed)
    or full URI for other protocols (e.g., ipfs://).

    @example "exampleyield.com/tbill" or "ipfs://QmXxxx"
    """

    category: str
    """
    The category of the link.
    Allowed values: "website", "social", "docs", "other"

    @example "website"
    """

    title: str
    """
    A human-readable label for the link.
    Any UTF-8 string.

    @example "Product Page"
    """


class MPTokenMetadata(TypedDict, total=False):
    """
    MPTokenMetadata object as per the XLS-89 standard.
    Represents metadata for a Multi-Purpose Token using long-form field names.
    This format is more human-readable and is recommended for client-side usage.
    Use {@link encodeMPTokenMetadata} utility function to convert to a compact hex string for on-ledger storage.
    Use {@link decodeMPTokenMetadata} utility function to convert from a hex string to this format.
    """

    ticker: str
    """
    Ticker symbol used to represent the token.
    Uppercase letters (A-Z) and digits (0-9) only. Max 6 characters recommended.

    @example "TBILL"
    """

    name: str
    """
    Display name of the token.
    Any UTF-8 string.

    @example "T-Bill Yield Token"
    """

    icon: str
    """
    URI to the token icon.
    Can be a `hostname/path` (HTTPS assumed) or full URI for other protocols (e.g., ipfs://).

    @example "example.org/token-icon.png" or "ipfs://QmXxxx"
    """

    asset_class: str
    """
    Top-level classification of token purpose.
    Allowed values: "rwa", "memes", "wrapped", "gaming", "defi", "other"

    @example "rwa"
    """

    issuer_name: str
    """
    The name of the issuer account.
    Any UTF-8 string.

    @example "Example Yield Co."
    """

    desc: Optional[str]
    """
    Short description of the token.
    Any UTF-8 string.

    @example "A yield-bearing stablecoin backed by short-term U.S. Treasuries"
    """

    asset_subclass: Optional[str]
    """
    Optional subcategory of the asset class.
    Required if `asset_class` is "rwa".
    Allowed values: "stablecoin", "commodity", "real_estate",
    "private_credit", "equity", "treasury", "other"

    @example "treasury"
    """

    uris: Optional[List[MPTokenMetadataUri]]
    """
    List of related URIs (site, dashboard, social media, documentation, etc.).
    Each URI object contains the link, its category, and a human-readable title.
    """

    additional_info: Optional[Union[str, Dict[str, Any]]]
    """
    Freeform field for key token details like interest rate,
    maturity date, term, or other relevant info.
    Can be any valid JSON object or UTF-8 string.

    @example { "interest_rate": "5.00%", "maturity_date": "2045-06-30" }
    """


class MPTokenIssuanceCreateFlag(int, Enum):
    """
    Transactions of the MPTokenIssuanceCreate type support additional values in the
    Flags field.
    This enum represents those options.
    """

    TF_MPT_CAN_LOCK = 0x00000002
    TF_MPT_REQUIRE_AUTH = 0x00000004
    TF_MPT_CAN_ESCROW = 0x00000008
    TF_MPT_CAN_TRADE = 0x00000010
    TF_MPT_CAN_TRANSFER = 0x00000020
    TF_MPT_CAN_CLAWBACK = 0x00000040


class MPTokenIssuanceCreateFlagInterface(TransactionFlagInterface):
    """
    Transactions of the MPTokenIssuanceCreate type support additional values in the
    Flags field.
    This TypedDict represents those options.
    """

    TF_MPT_CAN_LOCK: bool
    TF_MPT_REQUIRE_AUTH: bool
    TF_MPT_CAN_ESCROW: bool
    TF_MPT_CAN_TRADE: bool
    TF_MPT_CAN_TRANSFER: bool
    TF_MPT_CAN_CLAWBACK: bool


@require_kwargs_on_init
@dataclass(frozen=True)
class MPTokenIssuanceCreate(Transaction):
    """
    The MPTokenIssuanceCreate transaction creates a MPTokenIssuance object
    and adds it to the relevant directory node of the creator account.
    This transaction is the only opportunity an issuer has to specify any token fields
    that are defined as immutable (e.g., MPT Flags). If the transaction is successful,
    the newly created token will be owned by the account (the creator account) which
    executed the transaction.
    """

    asset_scale: Optional[int] = None
    """
    An asset scale is the difference, in orders of magnitude, between a standard unit
    and a corresponding fractional unit. More formally, the asset scale is a
    non-negative integer (0, 1, 2, …) such that one standard unit equals 10^(-scale) of
    a corresponding fractional unit. If the fractional unit equals the standard unit,
    then the asset scale is 0.
    Note that this value is optional, and will default to 0 if not supplied.
    """

    maximum_amount: Optional[str] = None
    """
    Specifies the maximum asset amount of this token that should ever be issued.
    It is a non-negative integer string that can store a range of up to 63 bits. If
    not set, the max amount will default to the largest unsigned 63-bit integer
    (0x7FFFFFFFFFFFFFFF)
    """

    transfer_fee: Optional[int] = None
    """
    Specifies the fee to charged by the issuer for secondary sales of the Token,
    if such sales are allowed. Valid values for this field are between 0 and 50,000
    inclusive, allowing transfer rates of between 0.000% and 50.000% in increments of
    0.001. The field must NOT be present if the `tfMPTCanTransfer` flag is not set.
    """

    mptoken_metadata: Optional[str] = None
    """
    Optional arbitrary metadata about this issuance, encoded as a hex string and
    limited to 1024 bytes.

    The decoded value must be a UTF-8 encoded JSON object that adheres to the
    XLS-89d MPTokenMetadata standard.

    While adherence to the XLS-89d format is not mandatory, non-compliant metadata
    may not be discoverable by ecosystem tools such as explorers and indexers.
    """

    transaction_type: TransactionType = field(
        default=TransactionType.MPTOKEN_ISSUANCE_CREATE,
        init=False,
    )

    def _get_errors(self: Self) -> Dict[str, str]:
        errors = super()._get_errors()

        if self.transfer_fee is not None:
            if not self.has_flag(MPTokenIssuanceCreateFlag.TF_MPT_CAN_TRANSFER):
                errors["transfer_fee"] = (
                    "Field cannot be provided without enabling tfMPTCanTransfer flag."
                )
            if self.transfer_fee < 0 or self.transfer_fee > _MAX_TRANSFER_FEE:
                errors["transfer_fee"] = "Field must be between 0 and " + str(
                    _MAX_TRANSFER_FEE
                )

        if self.mptoken_metadata is not None and (
            len(self.mptoken_metadata) == 0
            or len(self.mptoken_metadata) > MAX_MPTOKEN_METADATA_LENGTH
            or not HEX_REGEX.fullmatch(self.mptoken_metadata)
        ):
            errors["mptoken_metadata"] = (
                "Metadata must be valid non-empty hex string less than 1024 bytes "
                "(alternatively, 2048 hex characters)."
            )

        if self.mptoken_metadata is not None:
            validation_messages = validate_mptoken_metadata(self.mptoken_metadata)

            if len(validation_messages) > 0:
                message = "\n".join(
                    [MPT_META_WARNING_HEADER]
                    + [f"- {msg}" for msg in validation_messages]
                )
                warnings.warn(message, stacklevel=5)

        return errors
