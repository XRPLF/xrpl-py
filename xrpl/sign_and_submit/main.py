"""High-level sign-and-submit methods with XRPL transactions."""

from typing import Any, Callable, Dict

from xrpl.binarycodec import encode, encode_for_signing
from xrpl.keypairs.main import sign
from xrpl.models.requests import Request
from xrpl.models.requests.transactions.submit_only import SubmitOnly
from xrpl.models.response import Response
from xrpl.models.transactions import Transaction
from xrpl.sign_and_submit.utils import json_to_response
from xrpl.sign_and_submit.wallet import Wallet


def sign_and_submit_transaction(
    transaction: Transaction,
    wallet: Wallet,
    url: str,
    send_transaction: Callable[[str, Dict[str, Any]], Response],
) -> Response:
    """
    Signs a transaction and submits it to the XRPL.

    Args:
        transaction: the transaction to be signed and submitted.
        wallet: the wallet with which to sign the transaction.
        url: the rippled API endpoint URL.
        send_transaction: the function with which to submit the transaction.

    Returns:
        The response from the ledger.
    """
    tx_blob = sign_transaction(transaction, wallet)
    return submit_transaction_blob(tx_blob, url, send_transaction)


def sign_transaction(transaction: Transaction, wallet: Wallet) -> str:
    """
    Signs a transaction.

    Args:
        transaction: the transaction to be signed.
        wallet: the wallet with which to sign the transaction.

    Returns:
        The signed transaction blob.
    """
    # Increment the wallet sequence number, since we're about to use one.
    wallet.next_sequence_num += 1
    transaction_json = _prepare_transaction_json_for_binary_codec(transaction.to_dict())
    transaction_json["SigningPubKey"] = wallet.pub_key
    serialized_for_signing = encode_for_signing(transaction_json)
    serialized_bytes = bytes.fromhex(serialized_for_signing)
    signature = sign(serialized_bytes, wallet.priv_key)
    transaction_json["TxnSignature"] = signature
    return encode(transaction_json)


def submit_transaction_blob(
    transaction_blob: str,
    url: str,
    send_transaction: Callable[[str, Request], Response],
) -> Response:
    """
    Submits a transaction blob to the ledger.

    Args:
        transaction_blob: the transaction blob to be submitted.
        url: the rippled API endpoint URL.
        send_transaction: the function with which to submit the transaction.

    Returns:
        The response from the ledger.
    """
    # TODO: use our model objects when those are implemented for `submit`
    submit_request = SubmitOnly(tx_blob=transaction_blob)
    response = send_transaction(url, submit_request)
    return json_to_response(response.json())


def _prepare_transaction_json_for_binary_codec(dictionary: dict) -> dict:
    """
    Returns a new dictionary in which the first letter of every original key is
    capitalized.
    """
    formatted_dict = {
        _snake_to_capital_camel(key): value for (key, value) in dictionary.items()
    }
    return formatted_dict


def _snake_to_capital_camel(field: str) -> str:
    """Transforms snake case to capitalized camel case.
    For example, 'transaction_type' becomes 'TransactionType'.
    """
    words = field.split("_")
    capitalized_words = [word.capitalize() for word in words]
    return "".join(capitalized_words)
