"""Model for XChainAddClaimAttestation transaction type."""

from dataclasses import dataclass, field
from typing import Optional
from xrpl.models.transactions.types import TransactionType
from xrpl.models.utils import REQUIRED
from xrpl.models.transactions.transaction import Transaction
from xrpl.models.xchain_bridge import XChainBridge
from xrpl.models.utils import require_kwargs_on_init


@require_kwargs_on_init
@dataclass(frozen=True)
class XChainAddClaimAttestation(Transaction):
    """
    The XChainAddClaimAttestation transaction provides proof from a witness server,
    attesting to an XChainCommit transaction.  The signature must be from one of the keys on
    the door's signer list at the time the signature was provided. However, if the signature
    list changes between the time the signature was submitted and the quorum is reached, the
    new signature set is used and some of the currently collected signatures may be removed.
    Any account can submit signatures.
    """

    transaction_type: TransactionType = field(
        default=TransactionType.XCHAIN_ADD_CLAIM_ATTESTATION, init=False
    )

    amount: str = REQUIRED
    """
    The amount committed by the XChainCommit transaction on the source chain.
    """

    attestation_reward_account: str = REQUIRED
    """
    The account that should receive this signer's share of the SignatureReward.
    """

    attestation_signer_account: str = REQUIRED
    """
    The account on the door account's signer list that is signing the transaction.
    """

    destination: Optional[str] = None
    """
    (Optional) The destination account for the funds on the destination chain (taken from
    the XChainCommit transaction).
    """

    other_chain_source: str = REQUIRED
    """
    The account on the source chain that submitted the XChainCommit transaction that
    triggered the event associated with the attestation.
    """

    public_key: str = REQUIRED
    """
    The public key used to verify the attestation signature.
    """

    signature: str = REQUIRED
    """
    The signature attesting to the event on the other chain.
    """

    was_locking_chain_send: int = REQUIRED
    """
    A boolean representing the chain where the event occurred.
    """

    x_chain_bridge: XChainBridge = REQUIRED
    x_chain_claim_id: str = REQUIRED
    """
    The XChainClaimID associated with the transfer, which was included in the XChainCommit
    transaction.
    """
