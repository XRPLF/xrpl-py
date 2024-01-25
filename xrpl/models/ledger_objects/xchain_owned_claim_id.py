"""Models for the Ledger Object `XChainOwnedClaimID`"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional, Union

from xrpl.models.ledger_objects.ledger_entry_type import LedgerEntryType
from xrpl.models.ledger_objects.ledger_object import LedgerObject
from xrpl.models.nested_model import NestedModel
from xrpl.models.required import REQUIRED
from xrpl.models.utils import require_kwargs_on_init
from xrpl.models.xchain_bridge import XChainBridge


@require_kwargs_on_init
@dataclass(frozen=True)
class XChainOwnedClaimID(LedgerObject):
    """The model for the `XChainOwnedClaimID` Ledger Object"""

    account: str = REQUIRED  # type: ignore
    """
    The account that owns this object. This field is required.
    """

    ledger_index: str = REQUIRED  # type: ignore
    """
    The ledger index is a hash of a unique prefix for `XChainOwnedClaimID`s, the actual
    `XChainClaimID` value, and the fields in `XChainBridge`. This field is required.
    """

    other_chain_source: str = REQUIRED  # type: ignore
    """
    The account that must send the corresponding `XChainCommit` on the source chain. The
    destination may be specified in the `XChainCommit` transaction, which means that if
    the `OtherChainSource` isn't specified, another account can try to specify a
    different destination and steal the funds. This also allows tracking only a single
    set of signatures, since we know which account will send the `XChainCommit`
    transaction. This field is required.
    """

    signature_reward: str = REQUIRED  # type: ignore
    """
    The total amount to pay the witness servers for their signatures. It must be at
    least the value of `SignatureReward` in the `Bridge` ledger object.
    This field is required.
    """

    xchain_bridge: XChainBridge = REQUIRED  # type: ignore
    """
    The door accounts and assets of the bridge this object correlates to.
    This field is required.
    """

    xchain_claim_attestations: List[XChainClaimProofSig] = REQUIRED  # type: ignore
    """
    Attestations collected from the witness servers. This includes the parameters
    needed to recreate the message that was signed, including the amount, which chain
    (locking or issuing), optional destination, and reward account for that signature.
    This field is required.
    """

    xchain_claim_id: Union[int, str] = REQUIRED  # type: ignore
    """
    The unique sequence number for a cross-chain transfer. This field is required.
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

    flags: int = 0
    """
    Flags is always 0 since there are no flags defined for Chain entries.
    """

    ledger_entry_type: LedgerEntryType = field(
        default=LedgerEntryType.XCHAIN_OWNED_CLAIM_ID,
        init=False,
    )


@require_kwargs_on_init
@dataclass(frozen=True)
class XChainClaimProofSig(NestedModel):
    """A model for the `XChainClaimProofSig` object"""

    amount: str = REQUIRED  # type: ignore
    """
    The amount to claim in the `XChainCommit` transaction on the destination chain.
    This field is required.
    """

    attestation_reward_account: str = REQUIRED  # type: ignore
    """
    The account that should receive this signer's share of the `SignatureReward`.
    This field is required.
    """

    attestation_signer_account: str = REQUIRED  # type: ignore
    """
    The account on the door account's signer list that is signing the transaction.
    This field is required.
    """

    destination: Optional[str] = None
    """
    The destination account for the funds on the destination chain.
    """

    public_key: str = REQUIRED  # type: ignore
    """
    The public key used to verify the signature. This field is required.
    """

    was_locking_chain_send: int = REQUIRED  # type: ignore
    """
    A boolean representing the chain where the event occurred.
    This field is required.
    """
