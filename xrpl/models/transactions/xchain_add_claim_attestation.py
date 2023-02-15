"""Model for a XChainAddClaimAttestation transaction type."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional, Union

from typing_extensions import Literal

from xrpl.models.amounts import Amount
from xrpl.models.required import REQUIRED
from xrpl.models.transactions.transaction import Transaction
from xrpl.models.transactions.types import TransactionType
from xrpl.models.utils import require_kwargs_on_init
from xrpl.models.xchain_bridge import XChainBridge


@require_kwargs_on_init
@dataclass(frozen=True)
class XChainAddClaimAttestation(Transaction):
    """Represents a XChainAddClaimAttestation transaction."""

    xchain_bridge: XChainBridge = REQUIRED  # type: ignore

    public_key: str = REQUIRED  # type: ignore

    signature: str = REQUIRED  # type: ignore

    other_chain_source: str = REQUIRED  # type: ignore

    amount: Amount = REQUIRED  # type: ignore

    attestation_reward_account: str = REQUIRED  # type: ignore

    attestation_signer_account: str = REQUIRED  # type: ignore

    was_locking_chain_send: Union[Literal[0], Literal[1]] = REQUIRED  # type: ignore

    xchain_claim_id: str = REQUIRED  # type: ignore

    destination: Optional[str] = None

    transaction_type: TransactionType = field(
        default=TransactionType.XCHAIN_ADD_CLAIM_ATTESTATION,
        init=False,
    )
