"""
An account in the XRP Ledger represents a holder of XRP and a sender of transactions.
These request objects represent network client interactions that work with account info.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, List, Optional, Union

from xrpl.models.requests.request import Request, RequestMethod


@dataclass(frozen=True)
class AccountRequest(Request):
    """
    An account in the XRP Ledger represents a holder of XRP and a sender of
    transactions. These request objects represent network client interactions that work
    with account info.
    """

    account: str
    ledger_hash: Optional[str] = None
    ledger_index: Optional[Union[str, int]] = None


@dataclass(frozen=True)
class AccountChannelsRequest(AccountRequest):
    """
    This request returns information about an account's Payment Channels. This includes
    only channels where the specified account is the channel's source, not the
    destination. (A channel's "source" and "owner" are the same.)

    All information retrieved is relative to a particular version of the ledger.

    `See account_channels <https://xrpl.org/account_channels.html>`_
    """

    method: RequestMethod = field(
        default_factory=lambda: RequestMethod.AccountChannels, init=False
    )
    destination_account: Optional[str] = None
    limit: int = 200
    marker: Optional[Any] = None


@dataclass(frozen=True)
class AccountCurrenciesRequest(AccountRequest):
    """
    This request retrieves a list of currencies that an account can send or receive,
    based on its trust lines.

    This is not a thoroughly confirmed list, but it can be used to populate user
    interfaces.

    `See account_currencies <https://xrpl.org/account_currencies.html>`_
    """

    method: RequestMethod = field(
        default_factory=lambda: RequestMethod.AccountCurrencies, init=False
    )
    strict: bool = False


@dataclass(frozen=True)
class AccountInfoRequest(AccountRequest):
    """
    This request retrieves information about an account, its activity, and its XRP
    balance.

    All information retrieved is relative to a particular version of the ledger.

    `See account_info <https://xrpl.org/account_info.html>`_
    """

    method: RequestMethod = field(
        default_factory=lambda: RequestMethod.AccountInfo, init=False
    )
    queue: bool = False
    signer_lists: bool = False
    strict: bool = False


@dataclass(frozen=True)
class AccountLinesRequest(AccountRequest):
    """
    This request returns information about an account's trust lines, including balances
    in all non-XRP currencies and assets. All information retrieved is relative to a
    particular version of the ledger.

    `See account_lines <https://xrpl.org/account_lines.html>`_
    """

    method: RequestMethod = field(
        default_factory=lambda: RequestMethod.AccountLines, init=False
    )
    peer: Optional[str] = None
    limit: Optional[int] = None
    marker: Optional[Any] = None


class AccountObjectType(str, Enum):
    """Represents the object types that an AccountObjectsRequest can ask for."""

    Check = "check"
    DepositPreauth = "deposit_preauth"
    Escrow = "escrow"
    Offer = "offer"
    PaymentChannel = "payment_channel"
    SignerList = "signer_list"
    State = "state"
    Ticket = "ticket"


@dataclass(frozen=True)
class AccountObjectsRequest(AccountRequest):
    """
    This request returns the raw ledger format for all objects owned by an account.

    For a higher-level view of an account's trust lines and balances, see
    AccountLinesRequest instead.

    `See account_objects <https://xrpl.org/account_objects.html>`_
    """

    method: RequestMethod = field(
        default_factory=lambda: RequestMethod.AccountObjects, init=False
    )
    type: Optional[AccountObjectType] = None
    deletion_blockers_only: bool = False
    limit: Optional[int] = None
    marker: Optional[Any] = None


@dataclass(frozen=True)
class AccountOffersRequest(AccountRequest):
    """
    This request retrieves a list of offers made by a given account that are
    outstanding as of a particular ledger version.

    `See account_offers <https://xrpl.org/account_offers.html>`_
    """

    method: RequestMethod = field(
        default_factory=lambda: RequestMethod.AccountOffers, init=False
    )
    limit: Optional[int] = None
    marker: Optional[Any] = None
    strict: bool = False


@dataclass(frozen=True)
class AccountTransactionsRequest(AccountRequest):
    """
    This request retrieves from the ledger a list of transactions that involved the
    specified account.

    `See account_tx <https://xrpl.org/account_tx.html>`_
    """

    method: RequestMethod = field(
        default_factory=lambda: RequestMethod.AccountTransactions, init=False
    )
    ledger_index_min: Optional[int] = None
    ledger_index_max: Optional[int] = None
    binary: bool = False
    forward: bool = False
    limit: Optional[int] = None
    marker: Optional[Any] = None


@dataclass(frozen=True)
class GatewayBalancesRequest(AccountRequest):
    """
    This request calculates the total balances issued by a given account, optionally
    excluding amounts held by operational addresses.

    `See gateway_balances <https://xrpl.org/gateway_balances.html>`_
    """

    method: RequestMethod = field(
        default_factory=lambda: RequestMethod.GatewayBalances, init=False
    )
    strict: bool = False
    hotwallet: Optional[str, List[str]] = None


class NoRippleCheckRole(str, Enum):
    """Represents the options for the address role in a NoRippleCheckRequest."""

    Gateway = "gateway"
    User = "user"


@dataclass(frozen=True)
class NoRippleCheckRequest(AccountRequest):
    """
    This request provides a quick way to check the status of the Default Ripple field
    for an account and the No Ripple flag of its trust lines, compared with the
    recommended settings.

    `See noripple_check <https://xrpl.org/noripple_check.html>`_
    """

    method: RequestMethod = field(
        default_factory=lambda: RequestMethod.NoRippleCheck, init=False
    )
    role: NoRippleCheckRole
    transactions: bool = False
    limit: Optional[int] = 300
