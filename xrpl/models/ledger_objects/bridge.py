"""Models for the Ledger Object `Bridge`"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional, Union

from xrpl.models.ledger_objects.ledger_entry_type import LedgerEntryType
from xrpl.models.ledger_objects.ledger_object import LedgerObject
from xrpl.models.required import REQUIRED
from xrpl.models.utils import require_kwargs_on_init
from xrpl.models.xchain_bridge import XChainBridge


@require_kwargs_on_init
@dataclass(frozen=True)
class Bridge(LedgerObject):
    """The model for the `Bridge` Ledger Object"""

    account: str = REQUIRED  # type: ignore
    """
    The account that submitted the `XChainCreateBridge` transaction on the blockchain.
    This field is required.
    """

    min_account_create_amount: Optional[str] = None
    """
    The minimum amount, in XRP, required for an `XChainAccountCreateCommit` transaction.
    If this isn't present, the `XChainAccountCreateCommit` transaction will fail.
    This field can only be present on XRP-XRP bridges.
    """

    signature_reward: str = REQUIRED  # type: ignore
    """
    The total amount, in XRP, to be rewarded for providing a signature for cross-chain
    transfer or for signing for the cross-chain reward. This amount will be split among
    the signers. This field is required.
    """

    xchain_account_claim_count: Union[int, str] = REQUIRED  # type: ignore
    """
    A counter used to order the execution of account create transactions. It is
    incremented every time a `XChainAccountCreateCommit` transaction is "claimed" on the
    destination chain. When the "claim" transaction is run on the destination chain,
    the XChainAccountClaimCount must match the value that the XChainAccountCreateCount
    had at the time the XChainAccountClaimCount was run on the source chain. This
    orders the claims so that they run in the same order that the
    `XChainAccountCreateCommit` transactions ran on the source chain, to prevent
    transaction replay. This field is required.
    """

    xchain_account_create_count: Union[int, str] = REQUIRED  # type: ignore
    """
    A counter used to order the execution of account create transactions. It is
    incremented every time a successful `XChainAccountCreateCommit` transaction is run
    for the source chain. This field is required.
    """

    xchain_bridge: XChainBridge = REQUIRED  # type: ignore
    """
    A counter used to order the execution of account create transactions. It is
    incremented every time a successful `XChainAccountCreateCommit` transaction is run
    for the source chain. This field is required.
    """

    xchain_claim_id: Union[int, str] = REQUIRED  # type: ignore
    """
    The value of the next `XChainClaimID` to be created. This field is required.
    """

    owner_node: str = REQUIRED  # type: ignore
    """
    A hint indicating which page of the sender's owner directory links to this entry,
    in case the directory consists of multiple pages.
    """

    previous_txn_id: str = REQUIRED  # type: ignore
    """
    The identifying hash of the transaction that most recently modified this object.
    This field is required.
    """

    previous_txn_lgr_seq: int = REQUIRED  # type: ignore
    """
    The index of the ledger that contains the transaction that most recently modified
    this object.
    """

    flags: int = REQUIRED  # type: ignore
    """
    A bit-map of boolean flags. Flags is always 0 since there are no flags defined for
    Chain entries. This field is required.
    """

    ledger_entry_type: LedgerEntryType = field(
        default=LedgerEntryType.BRIDGE,
        init=False,
    )
