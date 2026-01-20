"""Model for LoanBrokerSet transaction type."""

from __future__ import annotations  # Requires Python 3.7+

from dataclasses import dataclass, field
from typing import Dict, Optional

from typing_extensions import Self

from xrpl.constants import HEX_REGEX
from xrpl.models.required import REQUIRED
from xrpl.models.transactions.transaction import Transaction
from xrpl.models.transactions.types import TransactionType
from xrpl.models.utils import KW_ONLY_DATACLASS, require_kwargs_on_init


@require_kwargs_on_init
@dataclass(frozen=True, **KW_ONLY_DATACLASS)
class LoanBrokerSet(Transaction):
    """This transaction creates and updates a Loan Broker"""

    vault_id: str = REQUIRED
    """
    The Vault ID that the Lending Protocol will use to access liquidity.
    This field is required.
    """

    loan_broker_id: Optional[str] = None
    """
    The Loan Broker ID that the transaction is modifying.
    """

    data: Optional[str] = None
    """
    Arbitrary metadata in hex format. The field is limited to 256 bytes.
    """

    management_fee_rate: Optional[int] = None
    """
    The 1/10th basis point fee charged by the Lending Protocol Owner.
    Valid values are between 0 and 10000 inclusive.
    """

    debt_maximum: Optional[str] = None
    """
    The maximum amount the protocol can owe the Vault.
    The default value of 0 means there is no limit to the debt. Must not be negative.
    """

    cover_rate_minimum: Optional[int] = None
    """
    The 1/10th basis point DebtTotal that the first loss capital must cover.
    Valid values are between 0 and 100000 inclusive.
    """

    cover_rate_liquidation: Optional[int] = None
    """
    The 1/10th basis point of minimum required first loss capital liquidated to cover a
    Loan default. Valid values are between 0 and 100000 inclusive.
    """

    transaction_type: TransactionType = field(
        default=TransactionType.LOAN_BROKER_SET,
        init=False,
    )

    MAX_DATA_PAYLOAD_LENGTH = 256 * 2
    MAX_MANAGEMENT_FEE_RATE = 10_000
    MAX_COVER_RATE_MINIMUM = 100_000
    MAX_COVER_RATE_LIQUIDATION = 100_000
    MAX_DEBT_MAXIMUM = 9223372036854775807

    def _get_errors(self: Self) -> Dict[str, str]:
        errors = super()._get_errors()

        if self.data is not None and len(self.data) > self.MAX_DATA_PAYLOAD_LENGTH:
            errors["LoanBrokerSet:data"] = "Data must be less than 256 bytes."

        if self.data is not None and not HEX_REGEX.fullmatch(self.data):
            errors["LoanBrokerSet:data"] = "Data must be a valid hex string."

        if self.management_fee_rate is not None and (
            self.management_fee_rate < 0
            or self.management_fee_rate > self.MAX_MANAGEMENT_FEE_RATE
        ):
            errors["LoanBrokerSet:management_fee_rate"] = (
                "Management fee rate must be between 0 and 10_000 inclusive."
            )

        if self.cover_rate_minimum is not None and (
            self.cover_rate_minimum < 0
            or self.cover_rate_minimum > self.MAX_COVER_RATE_MINIMUM
        ):
            errors["LoanBrokerSet:cover_rate_minimum"] = (
                "Cover rate minimum must be between 0 and 100_000 inclusive."
            )

        if self.cover_rate_liquidation is not None and (
            self.cover_rate_liquidation < 0
            or self.cover_rate_liquidation > self.MAX_COVER_RATE_LIQUIDATION
        ):
            errors["LoanBrokerSet:cover_rate_liquidation"] = (
                "Cover rate liquidation must be between 0 and 100_000 inclusive."
            )
        if self.debt_maximum is not None and (
            int(self.debt_maximum) < 0 or int(self.debt_maximum) > self.MAX_DEBT_MAXIMUM
        ):
            errors["LoanBrokerSet:debt_maximum"] = (
                "Debt maximum must not be negative or greater than 9223372036854775807."
            )

        return errors
