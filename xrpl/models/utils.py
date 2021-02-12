"""Helper functions for the Models package."""

from typing import Any, Dict, Union

from xrpl.models import IssuedCurrency


def currency_amount_to_json_object(
    amount: Union[str, IssuedCurrency]
) -> Union[Dict[str, Any], str]:
    """
    Converts a currency amount to JSON object form.

    Args:
        amount: the string XRP amount or issued currency amount.

    Returns:
        A JSON-safe representation of the currency amount.
    """
    if isinstance(amount, str):
        return amount
    return amount.to_json_object()


def json_object_to_currency_amount(
    amount: Union[str, IssuedCurrency, Dict[str, Any]]
) -> Union[str, IssuedCurrency]:
    """
    Converts a currency amount to JSON object form.

    Args:
        amount: the string XRP amount or issued currency dictionary representation.

    Returns:
        An object representing the amount (str for XRP, IssuedCurrency for issued
            currency).
    """
    if isinstance(amount, dict):
        return IssuedCurrency.from_dict(amount)
    return amount
