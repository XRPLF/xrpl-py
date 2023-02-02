"""Model for a XChainAddAttestationBatch transaction type."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Union

from typing_extensions import Literal

from xrpl.models.amounts import Amount
from xrpl.models.base_model import BaseModel
from xrpl.models.nested_model import NestedModel
from xrpl.models.required import REQUIRED
from xrpl.models.transactions.transaction import Transaction
from xrpl.models.transactions.types import TransactionType
from xrpl.models.utils import require_kwargs_on_init
from xrpl.models.xchain_bridge import XChainBridge


@require_kwargs_on_init
@dataclass(frozen=True)
class XChainClaimAttestationBatchElement(NestedModel):
    """Represents a single claim attestation."""

    account: str = REQUIRED  # type: ignore

    amount: Amount = REQUIRED  # type: ignore

    attestation_reward_account: str = REQUIRED  # type: ignore

    destination: Optional[str] = None

    public_key: str = REQUIRED  # type: ignore

    signature: str = REQUIRED  # type: ignore

    was_locking_chain_send: Union[Literal[0], Literal[1]] = REQUIRED  # type: ignore

    xchain_claim_id: str = REQUIRED  # type: ignore


@require_kwargs_on_init
@dataclass(frozen=True)
class XChainCreateAccountAttestationBatchElement(NestedModel):
    """Represents a single account creation attestation."""

    account: str = REQUIRED  # type: ignore

    amount: Amount = REQUIRED  # type: ignore

    attestation_reward_account: str = REQUIRED  # type: ignore

    destination: str = REQUIRED  # type: ignore

    public_key: str = REQUIRED  # type: ignore

    signature: str = REQUIRED  # type: ignore

    signature_reward: Amount = REQUIRED  # type: ignore

    was_locking_chain_send: Union[Literal[0], Literal[1]] = REQUIRED  # type: ignore

    xchain_account_create_count: str = REQUIRED  # type: ignore


@require_kwargs_on_init
@dataclass(frozen=True)
class XChainAttestationBatch(BaseModel):
    """Represents a set of attestations from a single witness server."""

    xchain_bridge: XChainBridge = REQUIRED  # type: ignore

    xchain_claim_attestation_batch: List[XChainClaimAttestationBatchElement] = field(
        default_factory=list
    )

    xchain_create_account_attestation_batch: List[
        XChainCreateAccountAttestationBatchElement
    ] = field(default_factory=list)


@require_kwargs_on_init
@dataclass(frozen=True)
class XChainAddAttestationBatch(Transaction):
    """Represents a XChainAddAttestationBatch transaction."""

    xchain_attestation_batch: XChainAttestationBatch = REQUIRED  # type: ignore

    transaction_type: TransactionType = field(
        default=TransactionType.XCHAIN_ADD_ATTESTATION_BATCH,
        init=False,
    )

    def _get_errors(self: XChainAddAttestationBatch) -> Dict[str, str]:
        errors = super()._get_errors()

        batch = self.xchain_attestation_batch
        claim_batch = batch.xchain_claim_attestation_batch
        account_create_batch = batch.xchain_create_account_attestation_batch

        if len(claim_batch) + len(account_create_batch) > 8:
            errors["num_attestations"] = "Cannot have more than 8 attestations."

        return errors
