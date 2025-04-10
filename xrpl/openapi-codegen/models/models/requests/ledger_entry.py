"""Model for LedgerEntry request type."""

from dataclasses import dataclass, field
from typing import Optional, Union
from xrpl.models.requests.request import RequestMethod
from xrpl.models.utils import REQUIRED
from xrpl.models.bridge_entry_bridge import BridgeEntryBridge
from xrpl.models.oracle_entry_oracle import OracleEntryOracle
from xrpl.models.requests.base_ledger_entry import BaseLedgerEntryRequest
from xrpl.models.requests.base_request import BaseRequest
from xrpl.models.requests.ledger_entry_options import LedgerEntryRequestOptions
from xrpl.models.requests.lookup_by_ledger import LookupByLedgerRequest
from xrpl.models.ripple_state_entry_ripple_state import RippleStateEntryRippleState
from xrpl.models.utils import require_kwargs_on_init


@require_kwargs_on_init
@dataclass(frozen=True)
class LedgerEntry(
    BaseRequest,
    LookupByLedgerRequest,
    BaseLedgerEntryRequest,
    LedgerEntryRequestOptions,
):
    """
    The ledger_entry method returns a single ledger entry from the XRP Ledger in its raw
    format. All information retrieved is relative to a particular version of the ledger.
    Returns a LedgerEntryResponse
    """

    method: RequestMethod = field(default=RequestMethod.LEDGER_ENTRY, init=False)

    index: Optional[str] = None
    """
    The ledger entry ID of a single entry to retrieve from the ledger, as a 64-character
        (256-bit) hexadecimal string.
    """

    account_root: Optional[str] = None
    """
    The classic address of the AccountRoot entry to retrieve.
    """

    amm: Optional[Union[str, AMMEntryAmmOneOf]] = None
    bridge_account: str = REQUIRED
    """
    The account that submitted the XChainCreateBridge transaction on the blockchain.
    """

    bridge: BridgeEntryBridge = REQUIRED
    directory: Optional[Union[str, DirectoryNodeEntryDirectoryOneOf]] = None
    offer: Optional[Union[str, OfferEntryOfferOneOf]] = None
    oracle: Optional[OracleEntryOracle] = None
    ripple_state: Optional[RippleStateEntryRippleState] = None
    check: Optional[str] = None
    escrow: Optional[Union[str, EscrowEntryEscrowOneOf]] = None
    payment_channel: Optional[str] = None
    deposit_preauth: Optional[Union[str, DepositPreauthEntryDepositPreauthOneOf]] = None
    ticket: Optional[Union[str, TicketEntryTicketOneOf]] = None
    nft_page: Optional[str] = None
