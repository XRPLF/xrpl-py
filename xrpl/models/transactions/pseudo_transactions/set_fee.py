"""Model for SetFee pseudo-transaction type."""

from dataclasses import dataclass, field

from xrpl.models.required import REQUIRED
from xrpl.models.transactions.pseudo_transactions.pseudo_transaction import (
    PseudoTransaction,
)
from xrpl.models.transactions.types import PseudoTransactionType
from xrpl.models.utils import require_kwargs_on_init


@require_kwargs_on_init
@dataclass(frozen=True)
class SetFeeBase(PseudoTransaction):
    """
    A SetFee pseudo-transaction marks a change in `transaction cost
    <https://xrpl.org/transaction-cost.html>`_ or `reserve requirements
    <https://xrpl.org/reserves.html>`_ as a result of `Fee Voting
    <https://xrpl.org/fee-voting.html>`_.
    """

    transaction_type: PseudoTransactionType = field(
        default=PseudoTransactionType.SET_FEE,
        init=False,
    )


@require_kwargs_on_init
@dataclass(frozen=True)
class SetFeePreAmendment(SetFeeBase):
    """
    A SetFee pseudo-transaction marks a change in `transaction cost
    <https://xrpl.org/transaction-cost.html>`_ or `reserve requirements
    <https://xrpl.org/reserves.html>`_ as a result of `Fee Voting
    <https://xrpl.org/fee-voting.html>`_.

    Syntax used prior to the `XRPFees Amendment
    <https://xrpl.org/known-amendments.html#xrpfees>`_.
    """

    base_fee: str = REQUIRED  # type: ignore
    """
    The charge, in drops of XRP, for the reference transaction, as hex. (This is the
    transaction cost before scaling for load.) This field is required.

    :meta hide-value:
    """

    reference_fee_units: int = REQUIRED  # type: ignore
    """
    The cost, in fee units, of the reference transaction. This field is required.

    :meta hide-value:
    """

    reserve_base: int = REQUIRED  # type: ignore
    """
    The base reserve, in drops. This field is required.

    :meta hide-value:
    """

    reserve_increment: int = REQUIRED  # type: ignore
    """
    The incremental reserve, in drops. This field is required.

    :meta hide-value:
    """


@require_kwargs_on_init
@dataclass(frozen=True)
class SetFeePostAmendment(SetFeeBase):
    """
    A SetFee pseudo-transaction marks a change in `transaction cost
    <https://xrpl.org/transaction-cost.html>`_ or `reserve requirements
    <https://xrpl.org/reserves.html>`_ as a result of `Fee Voting
    <https://xrpl.org/fee-voting.html>`_.

    Updated by the `XRPFees Amendment
    <https://xrpl.org/known-amendments.html#xrpfees>`_
    """

    base_fee_drops: str = REQUIRED  # type: ignore
    """
    The charge, in drops of XRP, for the reference transaction, as hex. (This is the
    transaction cost before scaling for load.) This field is required.

    :meta hide-value:
    """

    reserve_base_drops: int = REQUIRED  # type: ignore
    """
    The base reserve, in drops. This field is required.

    :meta hide-value:
    """

    reserve_increment_drops: int = REQUIRED  # type: ignore
    """
    The incremental reserve, in drops. This field is required.

    :meta hide-value:
    """


class SetFee(SetFeePreAmendment, SetFeePostAmendment):
    """
    A SetFee pseudo-transaction marks a change in `transaction cost
    <https://xrpl.org/transaction-cost.html>`_ or `reserve requirements
    <https://xrpl.org/reserves.html>`_ as a result of `Fee Voting
    <https://xrpl.org/fee-voting.html>`_.

    The parameters are different depending on if this is before or after the
    `XRPFees Amendment<https://xrpl.org/known-amendments.html#xrpfees>`_.
    """

    pass
