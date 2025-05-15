"""
The ledger_entry method returns a single ledger
object from the XRP Ledger in its raw format.
See ledger format for information on the
different types of objects you can retrieve.
`See ledger entry <https://xrpl.org/ledger_entry.html>`_
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Union

from typing_extensions import Self

from xrpl.models.base_model import BaseModel
from xrpl.models.requests.request import LookupByLedgerRequest, Request, RequestMethod
from xrpl.models.required import REQUIRED
from xrpl.models.utils import KW_ONLY_DATACLASS, require_kwargs_on_init
from xrpl.models.xchain_bridge import XChainBridge


class LedgerEntryType(str, Enum):
    """Identifiers for on-ledger objects."""

    ACCOUNT = "account"
    AMENDMENTS = "amendments"
    AMM = "amm"
    BRIDGE = "bridge"
    CHECK = "check"
    CREDENTIAL = "credential"
    DELEGATE = "delegate"
    DEPOSIT_PREAUTH = "deposit_preauth"
    DIRECTORY = "directory"
    DID = "did"
    ESCROW = "escrow"
    FEE = "fee"
    HASHES = "hashes"
    OFFER = "offer"
    ORACLE = "oracle"
    PAYMENT_CHANNEL = "payment_channel"
    PERMISSIONED_DOMAIN = "permissioned_domain"
    SIGNER_LIST = "signer_list"
    STATE = "state"
    TICKET = "ticket"
    MPT_ISSUANCE = "mpt_issuance"
    MPTOKEN = "mptoken"
    NFT_OFFER = "nft_offer"


@require_kwargs_on_init
@dataclass(frozen=True, **KW_ONLY_DATACLASS)
class Credential(BaseModel):
    """Specify the Credential to retrieve. If a string, must be the ledger entry ID of
    the entry, as hexadecimal. If an object, requires subject, issuer, and
    credential_type sub-fields.
    """

    subject: str = REQUIRED  # type: ignore
    """The account that is the subject of the credential."""

    issuer: str = REQUIRED  # type: ignore
    """The account that issued the credential."""

    credential_type: str = REQUIRED  # type: ignore
    """The type of the credential, as issued."""


@require_kwargs_on_init
@dataclass(frozen=True, **KW_ONLY_DATACLASS)
class Delegate(BaseModel):
    """
    Required fields for requesting a Delegate ledger object if not querying by
    object ID.
    """

    account: str = REQUIRED  # type: ignore
    """
    The account that wants to authorize another account.

    :meta hide-value:
    """

    authorize: str = REQUIRED  # type: ignore
    """
    The authorized account.

    :meta hide-value:
    """


@require_kwargs_on_init
@dataclass(frozen=True, **KW_ONLY_DATACLASS)
class DepositPreauth(BaseModel):
    """
    Required fields for requesting a DepositPreauth if not querying by
    object ID.
    """

    owner: str = REQUIRED  # type: ignore
    """
    This field is required.

    :meta hide-value:
    """

    authorized: str = REQUIRED  # type: ignore
    """
    This field is required.

    :meta hide-value:
    """


@require_kwargs_on_init
@dataclass(frozen=True, **KW_ONLY_DATACLASS)
class Directory(BaseModel):
    """
    Required fields for requesting a DirectoryNode if not querying by
    object ID.
    """

    owner: str = REQUIRED  # type: ignore
    """
    This field is required.

    :meta hide-value:
    """

    dir_root: str = REQUIRED  # type: ignore
    """
    This field is required.

    :meta hide-value:
    """
    sub_index: Optional[int] = None


@require_kwargs_on_init
@dataclass(frozen=True, **KW_ONLY_DATACLASS)
class Escrow(BaseModel):
    """
    Required fields for requesting a Escrow if not querying by
    object ID.
    """

    owner: str = REQUIRED  # type: ignore
    """
    This field is required.

    :meta hide-value:
    """

    seq: int = REQUIRED  # type: ignore
    """
    This field is required.

    :meta hide-value:
    """


@require_kwargs_on_init
@dataclass(frozen=True, **KW_ONLY_DATACLASS)
class MPToken(BaseModel):
    """
    Required fields for requesting a MPToken Ledger Entry, if not querying by
    object ID.
    """

    mpt_issuance_id: str = REQUIRED  # type: ignore
    """
    This field is required.

    :meta hide-value:
    """

    account: str = REQUIRED  # type: ignore
    """
    This field is required.

    :meta hide-value:
    """


@require_kwargs_on_init
@dataclass(frozen=True, **KW_ONLY_DATACLASS)
class Offer(BaseModel):
    """
    Required fields for requesting a Offer if not querying by
    object ID.
    """

    account: str = REQUIRED  # type: ignore
    """
    This field is required.

    :meta hide-value:
    """

    seq: int = REQUIRED  # type: ignore
    """
    This field is required.

    :meta hide-value:
    """


@require_kwargs_on_init
@dataclass(frozen=True, **KW_ONLY_DATACLASS)
class Oracle(BaseModel):
    """
    Required fields for requesting a Price Oracle Ledger Entry, if not querying by
    object ID.
    """

    account: str = REQUIRED  # type: ignore
    """
    This field is required.

    :meta hide-value:
    """

    oracle_document_id: Union[str, int] = REQUIRED  # type: ignore
    """
    This field is required.

    :meta hide-value:
    """


@require_kwargs_on_init
@dataclass(frozen=True, **KW_ONLY_DATACLASS)
class PermissionedDomain(BaseModel):
    """
    Required fields for requesting a PermissionedDomain if not querying by
    object ID.
    """

    account: str = REQUIRED  # type: ignore
    seq: int = REQUIRED  # type: ignore


@require_kwargs_on_init
@dataclass(frozen=True)
class RippleState(BaseModel):
    """Required fields for requesting a RippleState if not querying by object ID."""

    accounts: List[str] = REQUIRED  # type: ignore
    """
    This field is required.

    :meta hide-value:
    """

    currency: str = REQUIRED  # type: ignore
    """
    This field is required.

    :meta hide-value:
    """


@require_kwargs_on_init
@dataclass(frozen=True, **KW_ONLY_DATACLASS)
class Ticket(BaseModel):
    """Required fields for requesting a Ticket if not querying by object ID."""

    owner: str = REQUIRED  # type: ignore
    """
    This field is required.

    :meta hide-value:
    """

    ticket_sequence: int = REQUIRED  # type: ignore
    """
    This field is required.

    :meta hide-value:
    """


@require_kwargs_on_init
@dataclass(frozen=True, **KW_ONLY_DATACLASS)
class XChainClaimID(XChainBridge):
    """Required fields for requesting an XChainClaimID if not querying by object ID."""

    xchain_claim_id: Union[int, str] = REQUIRED  # type: ignore
    """
    The `XChainClaimID` associated with a cross-chain transfer, which was created in an
    `XChainCreateClaimID` transaction. This field is required.

    :meta hide-value:
    """


@require_kwargs_on_init
@dataclass(frozen=True, **KW_ONLY_DATACLASS)
class XChainCreateAccountClaimID(XChainBridge):
    """
    Required fields for requesting an XChainCreateAccountClaimID if not querying by
    object ID.
    """

    xchain_create_account_claim_id: Union[int, str] = REQUIRED  # type: ignore
    """
    The `XChainCreateAccountClaimID` associated with a cross-chain account create. This
    field is required.

    :meta hide-value:
    """


@require_kwargs_on_init
@dataclass(frozen=True, **KW_ONLY_DATACLASS)
class LedgerEntry(Request, LookupByLedgerRequest):
    """
    The ledger_entry method returns a single ledger
    object from the XRP Ledger in its raw format.
    See ledger format for information on the
    different types of objects you can retrieve.
    `See ledger entry <https://xrpl.org/ledger_entry.html>`_
    """

    method: RequestMethod = field(default=RequestMethod.LEDGER_ENTRY, init=False)
    index: Optional[str] = None
    account_root: Optional[str] = None
    check: Optional[str] = None
    credential: Optional[Union[str, Credential]] = None
    delegate: Optional[Union[str, Delegate]] = None
    deposit_preauth: Optional[Union[str, DepositPreauth]] = None
    did: Optional[str] = None
    directory: Optional[Union[str, Directory]] = None
    escrow: Optional[Union[str, Escrow]] = None
    mpt_issuance: Optional[str] = None
    mptoken: Optional[Union[MPToken, str]] = None
    offer: Optional[Union[str, Offer]] = None
    oracle: Optional[Oracle] = None
    payment_channel: Optional[str] = None
    permissioned_domain: Optional[Union[str, PermissionedDomain]] = None
    ripple_state: Optional[RippleState] = None
    ticket: Optional[Union[str, Ticket]] = None
    bridge_account: Optional[str] = None
    bridge: Optional[XChainBridge] = None
    xchain_claim_id: Optional[Union[int, str, XChainClaimID]] = None
    xchain_create_account_claim_id: Optional[
        Union[int, str, XChainCreateAccountClaimID]
    ] = None

    binary: bool = False
    nft_page: Optional[str] = None
    """Must be the object ID of the NFToken page, as hexadecimal"""
    include_deleted: Optional[bool] = None
    """This parameter is supported only by Clio servers"""

    def _get_errors(self: Self) -> Dict[str, str]:
        errors = super()._get_errors()
        query_params = [
            param
            for param in [
                self.index,
                self.account_root,
                self.check,
                self.credential,
                self.delegate,
                self.deposit_preauth,
                self.did,
                self.directory,
                self.escrow,
                self.offer,
                self.mpt_issuance,
                self.mptoken,
                self.oracle,
                self.payment_channel,
                self.permissioned_domain,
                self.ripple_state,
                self.ticket,
                self.xchain_claim_id,
                self.xchain_create_account_claim_id,
            ]
            if param is not None
        ]
        if (
            len(query_params) != 1
            and self.bridge is None
            and self.bridge_account is None
        ):
            errors["LedgerEntry"] = "Must choose exactly one data to query"

        if (self.bridge is None) != (self.bridge_account is None):
            # assert that you either have both of these or neither
            errors["Bridge"] = "Must include both `bridge` and `bridge_account`."

        return errors
