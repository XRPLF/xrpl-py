"""Model for SetFee pseudo-transaction type."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

from xrpl.models.exceptions import XRPLModelException
from xrpl.models.transactions.pseudo_transactions.pseudo_transaction import (
    PseudoTransaction,
)
from xrpl.models.transactions.types import PseudoTransactionType
from xrpl.models.utils import require_kwargs_on_init


@require_kwargs_on_init
@dataclass(frozen=True)
class SetFee(PseudoTransaction):
    """
    A SetFee pseudo-transaction marks a change in `transaction cost
    <https://xrpl.org/transaction-cost.html>`_ or `reserve requirements
    <https://xrpl.org/reserves.html>`_ as a result of `Fee Voting
    <https://xrpl.org/fee-voting.html>`_.

    The parameters are different depending on if this is before or after the
    `XRPFees Amendment<https://xrpl.org/known-amendments.html#xrpfees>`_

    Before the XRPFees Amendment which was proposed in rippled 1.10.0
    base_fee, reference_fee_units, reserve_base, and reserve_increment
    were required fields.

    After the XRPFees Amendment, base_fee_drops, reserve_base_drops,
    and reserve_increment_drops are required fields.

    No SetFee Psuedo Transaction should contain fields from BOTH before
    and after the XRPFees amendment.
    """

    def __post_init__(self: SetFee) -> None:
        """
        Used to validate that SetFee is strictly following the correct syntax from
        before the XRPFees Amendment or after it has been enabled.

        Raises:
            XRPLModelException: if required fields are not provided.
        """
        if self.base_fee is None:
            # SetFee from AFTER XRPFees Amendment
            error_preamble = (
                "SetFee psuedotransactions from after the XRPFee amendment require "
            )
            if self.base_fee_drops is None:
                raise XRPLModelException(
                    error_preamble + "'base_fee_drops' to be defined."
                )
            if self.reserve_base_drops is None:
                raise XRPLModelException(
                    error_preamble + "'reserve_base_drops' to be defined."
                )
            if self.reserve_increment_drops is None:
                raise XRPLModelException(
                    error_preamble + "'reserve_increment_drops' to be defined."
                )
        else:
            # SetFee from BEFORE XRPFees Amendment
            error_preamble = (
                "SetFee psuedotransactions from before the XRPFee amendment require "
            )
            if self.reference_fee_units is None:
                raise XRPLModelException(
                    error_preamble + "'reference_fee_units' to be defined."
                )
            if self.reserve_base is None:
                raise XRPLModelException(
                    error_preamble + "'reserve_base' to be defined."
                )
            if self.reserve_increment is None:
                raise XRPLModelException(
                    error_preamble + "'reserve_increment' to be defined."
                )

        any_old_field_exists = (
            self.base_fee is not None
            or self.reference_fee_units is not None
            or self.reserve_base is not None
            or self.reserve_increment is not None
        )
        any_new_field_exists = (
            self.base_fee_drops is not None
            or self.reserve_base_drops is not None
            or self.reserve_increment_drops is not None
        )
        if any_old_field_exists and any_new_field_exists:
            raise XRPLModelException(
                f"SetFee psuedotransactions cannot mix parameters from before and "
                f"after XRPFees amendment. Please use the pre-XRPFees syntax ("
                f"base_fee, reference_fee_units, reserve_base, and reserve_increment) "
                f"OR the post-XRPFees syntax (base_fee_drops, "
                f"reserve_base_drops, and reserve_increment_drops), but not both."
                f"\nYour object defined: {self}"
            )

    # Required BEFORE the XRPFees Amendment

    base_fee: Optional[str] = None
    """
    The charge, in drops of XRP, for the reference transaction, as hex. (This is the
    transaction cost before scaling for load.) This field is required.

    :meta hide-value:
    """

    reference_fee_units: Optional[int] = None
    """
    The cost, in fee units, of the reference transaction. This field is required.

    :meta hide-value:
    """

    reserve_base: Optional[int] = None
    """
    The base reserve, in drops. This field is required.

    :meta hide-value:
    """

    reserve_increment: Optional[int] = None
    """
    The incremental reserve, in drops. This field is required.

    :meta hide-value:
    """

    # Required AFTER the XRPFees Amendment

    base_fee_drops: Optional[str] = None
    """
    The charge, in drops of XRP, for the reference transaction, as hex. (This is the
    transaction cost before scaling for load.) This field is required.

    :meta hide-value:
    """

    reserve_base_drops: Optional[str] = None
    """
    The base reserve, in drops. This field is required.

    :meta hide-value:
    """

    reserve_increment_drops: Optional[str] = None
    """
    The incremental reserve, in drops. This field is required.

    :meta hide-value:
    """

    transaction_type: PseudoTransactionType = field(
        default=PseudoTransactionType.SET_FEE,
        init=False,
    )
