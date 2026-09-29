"""Model for AMMClawback transaction type."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, Optional, Union

from typing_extensions import Self

from xrpl.models.amounts import ClawbackAmount, IssuedCurrencyAmount, MPTAmount
from xrpl.models.currencies import Currency, IssuedCurrency, MPTCurrency
from xrpl.models.required import REQUIRED
from xrpl.models.transactions.transaction import Transaction, TransactionFlagInterface
from xrpl.models.transactions.types import TransactionType
from xrpl.models.utils import get_mpt_issuer


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


@dataclass(frozen=True, kw_only=True)
class AMMClawback(Transaction):
    """
    Claw back tokens from a holder who has deposited your issued tokens into an AMM
    pool.
    """

    holder: str = REQUIRED
    """The account holding the asset to be clawed back."""

    asset: Union[IssuedCurrency, MPTCurrency] = REQUIRED
    """
    Specifies the asset that the issuer wants to claw back from the AMM pool. In JSON,
    this is an object with currency and issuer fields, or with an mpt_issuance_id field
    for an MPT. The asset's issuer must match Account.
    """

    asset2: Currency = REQUIRED
    """
    Specifies the other asset in the AMM's pool. In JSON, this is an object with
    currency and issuer fields (omit issuer for XRP).
    """

    amount: Optional[ClawbackAmount] = None
    """
    The maximum amount to claw back from the AMM account. It must be the same asset as
    Asset (matching currency and issuer, or mpt_issuance_id). If this field isn't
    specified, or the value subfield exceeds the holder's available tokens in the AMM,
    all of the holder's tokens are clawed back.
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

        if isinstance(self.asset, MPTCurrency):
            # An MPT's issuer is encoded in its issuance ID.
            asset_issuer = get_mpt_issuer(self.asset.mpt_issuance_id)
            amount_matches_asset = (
                isinstance(self.amount, MPTAmount)
                and self.amount.mpt_issuance_id.upper()
                == self.asset.mpt_issuance_id.upper()
            )
            amount_error = "Amount.mpt_issuance_id must match Asset.mpt_issuance_id."
        elif isinstance(self.asset, IssuedCurrency):
            asset_issuer = self.asset.issuer
            amount_matches_asset = (
                isinstance(self.amount, IssuedCurrencyAmount)
                and self.amount.issuer == self.asset.issuer
                and self.amount.currency == self.asset.currency
            )
            amount_error = (
                "Amount.issuer and Amount.currency must match corresponding Asset "
                + "fields."
            )
        else:
            # A wrongly-typed asset is already reported by the base type check.
            return errors if errors else None

        if self.account != asset_issuer:
            errors += (
                "Asset.issuer and AMMClawback transaction sender must be identical."
            )

        if self.amount is not None and not amount_matches_asset:
            errors += amount_error

        return errors if errors else None
