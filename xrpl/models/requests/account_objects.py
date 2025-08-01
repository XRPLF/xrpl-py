"""
This request returns the raw ledger format for all objects owned by an account.

For a higher-level view of an account's trust lines and balances, see
AccountLinesRequest instead.

`See account_objects <https://xrpl.org/account_objects.html>`_
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Optional

from xrpl.models.requests.request import LookupByLedgerRequest, Request, RequestMethod
from xrpl.models.required import REQUIRED
from xrpl.models.utils import KW_ONLY_DATACLASS, require_kwargs_on_init


class AccountObjectType(str, Enum):
    """Represents the object types that an AccountObjectsRequest can ask for."""

    AMM = "amm"
    BRIDGE = "bridge"
    CHECK = "check"
    CREDENTIAL = "credential"
    DEPOSIT_PREAUTH = "deposit_preauth"
    DELEGATE = "delegate"
    DID = "did"
    ESCROW = "escrow"
    MPT_ISSUANCE = "mpt_issuance"
    MPTOKEN = "mptoken"
    NFT_OFFER = "nft_offer"
    NFT_PAGE = "nft_page"
    OFFER = "offer"
    ORACLE = "oracle"
    PAYMENT_CHANNEL = "payment_channel"
    PERMISSIONED_DOMAIN = "permissioned_domain"
    SIGNER_LIST = "signer_list"
    STATE = "state"
    TICKET = "ticket"
    VAULT = "vault"
    XCHAIN_OWNED_CREATE_ACCOUNT_CLAIM_ID = "xchain_owned_create_account_claim_id"
    XCHAIN_OWNED_CLAIM_ID = "xchain_owned_claim_id"


@require_kwargs_on_init
@dataclass(frozen=True, **KW_ONLY_DATACLASS)
class AccountObjects(Request, LookupByLedgerRequest):
    """
    This request returns the raw ledger format for all objects owned by an account.

    For a higher-level view of an account's trust lines and balances, see
    AccountLinesRequest instead.

    `See account_objects <https://xrpl.org/account_objects.html>`_
    """

    account: str = REQUIRED  # type: ignore
    """
    This field is required.

    :meta hide-value:
    """

    method: RequestMethod = field(default=RequestMethod.ACCOUNT_OBJECTS, init=False)
    type: Optional[AccountObjectType] = None
    deletion_blockers_only: bool = False
    limit: Optional[int] = None
    # marker data shape is actually undefined in the spec, up to the
    # implementation of an individual server
    marker: Optional[Any] = None
