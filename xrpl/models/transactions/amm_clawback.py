"""Model for AMMClawback transaction type."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, Optional

from typing_extensions import Self

from xrpl.models.amounts import IssuedCurrencyAmount
from xrpl.models.currencies import Currency
from xrpl.models.currencies.issued_currency import IssuedCurrency
from xrpl.models.required import REQUIRED
from xrpl.models.transactions.transaction import Transaction, TransactionFlagInterface
from xrpl.models.transactions.types import TransactionType
from xrpl.models.utils import KW_ONLY_DATACLASS, require_kwargs_on_init


class AMMClawbackFlag(int, Enum):
    """
    Claw back the specified amount of Asset, and a corresponding amount of Asset2 based
    on the AMM pool's asset proportion; both assets must be issued by the issuer in the
    Account field. If this flag isn't enabled, the issuer claws back the specified
    amount of Asset, while a corresponding proportion of Asset2 goes back to the Holder.
    """

    TF_CLAW_TWO_ASSETS = 0x00000001


class AMMClawbackFlagInterface(TransactionFlagInterface):
    """
    Claw back the specified amount of Asset, and a corresponding amount of Asset2 based
    on the AMM pool's asset proportion; both assets must be issued by the issuer in the
    Account field. If this flag isn't enabled, the issuer claws back the specified
    amount of Asset, while a corresponding proportion of Asset2 goes back to the Holder.
    """

    TF_CLAW_TWO_ASSETS: bool


@require_kwargs_on_init
@dataclass(frozen=True, **KW_ONLY_DATACLASS)
class AMMClawback(Transaction):
    """
    Claw back tokens from a holder who has deposited your issued tokens into an AMM
    pool.
    """

    holder: str = REQUIRED  # type: ignore
    """The account holding the asset to be clawed back."""

    asset: IssuedCurrency = REQUIRED  # type: ignore
    """
    Specifies the asset that the issuer wants to claw back from the AMM pool. In JSON,
    this is an object with currency and issuer fields. The issuer field must match with
    Account.
    """

    asset2: Currency = REQUIRED  # type: ignore
    """
    Specifies the other asset in the AMM's pool. In JSON, this is an object with
    currency and issuer fields (omit issuer for XRP).
    """

    amount: Optional[IssuedCurrencyAmount] = None
    """
    The maximum amount to claw back from the AMM account. The currency and issuer
    subfields should match the Asset subfields. If this field isn't specified, or the
    value subfield exceeds the holder's available tokens in the AMM, all of the
    holder's tokens are clawed back.
    """

    transaction_type: TransactionType = field(
        default=TransactionType.AMM_CLAWBACK,
        init=False,
    )

    def _get_errors(self: Self) -> Dict[str, str]:
        return {
            key: value
            for key, value in {
                **super()._get_errors(),
                "AMMClawback": self._validate_wallet_and_amount_fields(),
            }.items()
            if value is not None
        }

    def _validate_wallet_and_amount_fields(self: Self) -> Optional[str]:
        errors = ""
        if self.account == self.holder:
            errors += "Issuer and holder wallets must be distinct."

        if self.account != self.asset.issuer:
            errors += (
                "Asset.issuer and AMMClawback transaction sender must be identical."
            )

        if self.amount is not None and (
            self.amount.issuer != self.asset.issuer
            or self.amount.currency != self.asset.currency
        ):
            errors += (
                "Amount.issuer and Amount.currency must match corresponding Asset "
                + "fields."
            )

        return errors if errors else None
