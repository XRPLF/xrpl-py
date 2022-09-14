"""Model for a XChainAddAttestation transaction type."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Type, Union

from typing_extensions import Literal

from xrpl.models.amounts import Amount
from xrpl.models.base_model import BaseModel
from xrpl.models.required import REQUIRED
from xrpl.models.transactions.transaction import Transaction
from xrpl.models.transactions.types import TransactionType
from xrpl.models.utils import require_kwargs_on_init
from xrpl.models.xchain_bridge import XChainBridge


@require_kwargs_on_init
@dataclass(frozen=True)
class XChainClaimAttestationBatchElement(BaseModel):
    """Represents a single claim attestation."""

    account: str = REQUIRED  # type: ignore

    amount: Amount = REQUIRED  # type: ignore

    attestation_reward_account: str = REQUIRED  # type: ignore

    destination: Optional[str] = None

    public_key: str = REQUIRED  # type: ignore

    signature: str = REQUIRED  # type: ignore

    was_locking_chain_send: Union[Literal[0, 1]] = REQUIRED  # type: ignore

    xchain_claim_id: str = REQUIRED  # type: ignore

    @classmethod
    def is_dict_of_model(
        cls: Type[XChainClaimAttestationBatchElement], dictionary: Dict[str, Any]
    ) -> bool:
        """
        Returns True if the input dictionary was derived by the `to_dict`
        method of an instance of this class. In other words, True if this is
        a dictionary representation of an instance of this class.

        NOTE: does not account for model inheritance, IE will only return True
        if dictionary represents an instance of this class, but not if
        dictionary represents an instance of a subclass of this class.

        Args:
            dictionary: The dictionary to check.

        Returns:
            True if dictionary is a dict representation of an instance of this
            class.
        """
        return (
            isinstance(dictionary, dict)
            and "xchain_claim_attestation_batch_element" in dictionary
            and super().is_dict_of_model(
                dictionary["xchain_claim_attestation_batch_element"]
            )
        )

    @classmethod
    def from_dict(
        cls: Type[XChainClaimAttestationBatchElement], value: Dict[str, Any]
    ) -> XChainClaimAttestationBatchElement:
        """
        Construct a new XChainClaimAttestationBatchElement from a dictionary of
        parameters.

        Args:
            value: The value to construct the XChainClaimAttestationBatchElement from.

        Returns:
            A new XChainClaimAttestationBatchElement object, constructed using the
            given parameters.
        """
        if len(value) == 1 and "xchain_claim_attestation_batch_element" in value:
            return super(XChainClaimAttestationBatchElement, cls).from_dict(
                value["xchain_claim_attestation_batch_element"]
            )
        return super(XChainClaimAttestationBatchElement, cls).from_dict(value)

    def to_dict(self: XChainClaimAttestationBatchElement) -> Dict[str, Any]:
        """
        Returns the dictionary representation of a XChainClaimAttestationBatchElement.

        Returns:
            The dictionary representation of a XChainClaimAttestationBatchElement.
        """
        return {"xchain_claim_attestation_batch_element": super().to_dict()}


@require_kwargs_on_init
@dataclass(frozen=True)
class XChainCreateAccountAttestationBatchElement(BaseModel):
    """Represents a single account creation attestation."""

    account: str = REQUIRED  # type: ignore

    amount: Amount = REQUIRED  # type: ignore

    attestation_reward_account: str = REQUIRED  # type: ignore

    destination: str = REQUIRED  # type: ignore

    public_key: str = REQUIRED  # type: ignore

    signature: str = REQUIRED  # type: ignore

    signature_reward: Amount = REQUIRED  # type: ignore

    was_locking_chain_send: Union[Literal[0, 1]] = REQUIRED  # type: ignore

    xchain_account_create_count: str = REQUIRED  # type: ignore

    @classmethod
    def is_dict_of_model(
        cls: Type[XChainCreateAccountAttestationBatchElement],
        dictionary: Dict[str, Any],
    ) -> bool:
        """
        Returns True if the input dictionary was derived by the `to_dict`
        method of an instance of this class. In other words, True if this is
        a dictionary representation of an instance of this class.

        NOTE: does not account for model inheritance, IE will only return True
        if dictionary represents an instance of this class, but not if
        dictionary represents an instance of a subclass of this class.

        Args:
            dictionary: The dictionary to check.

        Returns:
            True if dictionary is a dict representation of an instance of this
            class.
        """
        return (
            isinstance(dictionary, dict)
            and "xchain_create_account_attestation_batch_element" in dictionary
            and super().is_dict_of_model(
                dictionary["xchain_create_account_attestation_batch_element"]
            )
        )

    @classmethod
    def from_dict(
        cls: Type[XChainCreateAccountAttestationBatchElement], value: Dict[str, Any]
    ) -> XChainCreateAccountAttestationBatchElement:
        """
        Construct a new XChainCreateAccountAttestationBatchElement from a dictionary of
        parameters.

        Args:
            value: The value to construct the
                XChainCreateAccountAttestationBatchElement from.

        Returns:
            A new XChainCreateAccountAttestationBatchElement object, constructed using
            the given parameters.
        """
        if (
            len(value) == 1
            and "xchain_create_account_attestation_batch_element" in value
        ):
            return super(XChainCreateAccountAttestationBatchElement, cls).from_dict(
                value["xchain_create_account_attestation_batch_element"]
            )
        return super(XChainCreateAccountAttestationBatchElement, cls).from_dict(value)

    def to_dict(self: XChainCreateAccountAttestationBatchElement) -> Dict[str, Any]:
        """
        Returns the dictionary representation of a
        XChainCreateAccountAttestationBatchElement.

        Returns:
            The dictionary representation of a
            XChainCreateAccountAttestationBatchElement.
        """
        return {"xchain_create_account_attestation_batch_element": super().to_dict()}


@require_kwargs_on_init
@dataclass(frozen=True)
class XChainAttestationBatch(BaseModel):
    """Represents a set of attestations from a single witness server."""

    xchain_bridge: XChainBridge = REQUIRED  # type: ignore

    xchain_claim_attestation_batch: List[
        XChainClaimAttestationBatchElement
    ] = REQUIRED  # type: ignore

    xchain_create_account_attestation_batch: List[
        XChainCreateAccountAttestationBatchElement
    ] = REQUIRED  # type: ignore


@require_kwargs_on_init
@dataclass(frozen=True)
class XChainAddAttestation(Transaction):
    """Represents a XChainAddAttestation transaction."""

    xchain_attestation_batch: XChainAttestationBatch = REQUIRED  # type: ignore

    transaction_type: TransactionType = field(
        default=TransactionType.XCHAIN_ADD_ATTESTATION,
        init=False,
    )
