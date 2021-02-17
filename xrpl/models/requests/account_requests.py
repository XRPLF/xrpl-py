"""TODO: docstring"""

from dataclasses import dataclass, field
from typing import Any, Enum, List, Optional, Union

from xrpl.models.requests.request import Request, RequestMethod


@dataclass(frozen=True)
class AccountRequest(Request):
    """TODO: docstring"""

    account: str
    ledger_hash: Optional[str] = None
    ledger_index: Optional[Union[str, int]] = None


@dataclass(frozen=True)
class AccountChannelsRequest(AccountRequest):
    """TODO: docstring"""

    method: RequestMethod = field(
        default_factory=lambda: RequestMethod.AccountChannels, init=False
    )
    destination_account: Optional[str] = None
    limit: int = 200
    marker: Optional[Any] = None


@dataclass(frozen=True)
class AccountCurrenciesRequest(AccountRequest):
    """TODO: docstring"""

    method: RequestMethod = field(
        default_factory=lambda: RequestMethod.AccountCurrencies, init=False
    )
    strict: bool = False


@dataclass(frozen=True)
class AccountInfoRequest(AccountRequest):
    """TODO: docstring"""

    method: RequestMethod = field(
        default_factory=lambda: RequestMethod.AccountInfo, init=False
    )
    queue: bool = False
    signer_lists: bool = False
    strict: bool = False


@dataclass(frozen=True)
class AccountLinesRequest(AccountRequest):
    """TODO: docstring"""

    method: RequestMethod = field(
        default_factory=lambda: RequestMethod.AccountLines, init=False
    )
    peer: Optional[str] = None
    limit: Optional[int] = None
    marker: Optional[Any] = None


class AccountObjectType(str, Enum):
    """TODO: docstring"""

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
    """TODO: docstring"""

    method: RequestMethod = field(
        default_factory=lambda: RequestMethod.AccountObjects, init=False
    )
    type: Optional[AccountObjectType] = None
    deletion_blockers_only: bool = False
    limit: Optional[int] = None
    marker: Optional[Any] = None


@dataclass(frozen=True)
class AccountOffersRequest(AccountRequest):
    """TODO: docstring"""

    method: RequestMethod = field(
        default_factory=lambda: RequestMethod.AccountOffers, init=False
    )
    limit: Optional[int] = None
    marker: Optional[Any] = None
    strict: bool = False


@dataclass(frozen=True)
class AccountTransactionsRequest(AccountRequest):
    """TODO: docstring"""

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
    """TODO: docstring"""

    method: RequestMethod = field(
        default_factory=lambda: RequestMethod.GatewayBalances, init=False
    )
    strict: bool = False
    hotwallet: Optional[str, List[str]] = None


class NoRippleCheckRole(str, Enum):
    """TODO: docstring"""

    Gateway = "gateway"
    User = "user"


@dataclass(frozen=True)
class NoRippleCheckRequest(AccountRequest):
    """TODO: docstring"""

    method: RequestMethod = field(
        default_factory=lambda: RequestMethod.NoRippleCheck, init=False
    )
    role: NoRippleCheckRole
    transactions: bool = False
    limit: Optional[int] = 300
