"""Helper functions for the Models package."""

from typing import Any, Dict, Union

from xrpl.models.issued_currency import IssuedCurrency


def currency_amount_to_dict(
    amount: Union[str, IssuedCurrency]
) -> Union[Dict[str, Any], str]:
    """
    Converts a currency/XRP amount to dictionary form.

    Args:
        amount: the string XRP amount or issued currency amount.

    Returns:
        A JSON-safe dictionary representation of the currency amount.
    """
    if isinstance(amount, str):
        return amount
    return amount.to_dict()


def dict_to_currency_amount(
    amount: Union[str, IssuedCurrency, Dict[str, Any]]
) -> Union[str, IssuedCurrency]:
    """
    Converts a JSON-safe representation of a currency/XRP amount to a model
    representation.

    Args:
        amount: the string XRP amount or issued currency dictionary representation.

    Returns:
        An object representing the amount (str for XRP, IssuedCurrency for issued
            currency).
    """
    if isinstance(amount, dict):
        return IssuedCurrency.from_dict(amount)
    return amount
