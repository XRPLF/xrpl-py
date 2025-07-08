"""
A ClawbackAmount is an object specifying a currency, a quantity of that currency, and
the counterparty (issuer) on the trustline that holds the value. Clawback is possible
only for IOU Tokens and MPT Tokens. XRP Amounts cannot be clawed back.
"""

from typing import Union

from xrpl.models.amounts.issued_currency_amount import IssuedCurrencyAmount
from xrpl.models.amounts.mpt_amount import MPTAmount

ClawbackAmount = Union[IssuedCurrencyAmount, MPTAmount]
