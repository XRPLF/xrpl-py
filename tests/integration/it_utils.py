"""Utility functions for integration tests."""

from xrpl.models.response import Response
from xrpl.models.transactions.transaction import Transaction
from xrpl.network_clients import JsonRpcClient
from xrpl.sign_and_submit import sign_and_submit_transaction
from xrpl.wallet import Wallet

JSON_RPC_URL = "http://test.xrp.xpring.io:51234"
JSON_RPC_CLIENT = JsonRpcClient(JSON_RPC_URL)


def submit_transaction(transaction: Transaction, wallet: Wallet) -> Response:
    """Signs and submits a transaction to the XRPL."""
    return sign_and_submit_transaction(transaction, wallet, JSON_RPC_CLIENT.request)


def _prepare_transaction_json_for_binary_codec(dictionary: dict) -> dict:
    """
    Returns a new dictionary in which the keys have been formatted as
    CamelCase and standardized to be serialized by the binary codec.
    """
    formatted_dict = {
        _snake_to_capital_camel(key): value for (key, value) in dictionary.items()
    }
    # one-off conversion cases for transaction field names
    if "CheckId" in formatted_dict:
        formatted_dict["CheckID"] = formatted_dict["CheckId"]
        del formatted_dict["CheckId"]
    if "InvoiceId" in formatted_dict:
        formatted_dict["InvoiceID"] = formatted_dict["InvoiceId"]
        del formatted_dict["InvoiceId"]
    return formatted_dict


def _snake_to_capital_camel(field: str) -> str:
    """Transforms snake case to capitalized camel case.
    For example, 'transaction_type' becomes 'TransactionType'.
    """
    words = field.split("_")
    capitalized_words = [word.capitalize() for word in words]
    return "".join(capitalized_words)
