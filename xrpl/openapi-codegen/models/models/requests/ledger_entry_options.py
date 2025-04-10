from typing import Union
from xrpl.models.account_root_entry import AccountRootEntry
from xrpl.models.amm_entry import AMMEntry
from xrpl.models.bridge_entry import BridgeEntry
from xrpl.models.check_entry import CheckEntry
from xrpl.models.deposit_preauth_entry import DepositPreauthEntry
from xrpl.models.directory_node_entry import DirectoryNodeEntry
from xrpl.models.escrow_entry import EscrowEntry
from xrpl.models.ledger_entry_by_id import LedgerEntryByID
from xrpl.models.nft_page_entry import NFTPageEntry
from xrpl.models.offer_entry import OfferEntry
from xrpl.models.oracle_entry import OracleEntry
from xrpl.models.pay_channel_entry import PayChannelEntry
from xrpl.models.ripple_state_entry import RippleStateEntry
from xrpl.models.ticket_entry import TicketEntry

LedgerEntryRequestOptions = Union[AMMEntry, AccountRootEntry, BridgeEntry, CheckEntry, DepositPreauthEntry, DirectoryNodeEntry, EscrowEntry, LedgerEntryByID, NFTPageEntry, OfferEntry, OracleEntry, PayChannelEntry, RippleStateEntry, TicketEntry]

