"""High-level transaction methods with XRPL transactions."""
import re
from typing import Any, Dict, cast

from xrpl.clients import Client, XRPLRequestFailureException
from xrpl.core.binarycodec import encode, encode_for_signing
from xrpl.core.keypairs.main import sign
from xrpl.models.amounts import IssuedCurrencyAmount
from xrpl.models.requests import SubmitOnly
from xrpl.models.response import Response
from xrpl.models.transactions.transaction import Transaction
from xrpl.wallet import Wallet


def safe_sign_and_submit_transaction(
    transaction: Transaction,
    wallet: Wallet,
    client: Client,
) -> Response:
    """
    Signs a transaction (locally, without trusting external rippled nodes) and submits
    it to the XRPL.

    Args:
        transaction: the transaction to be signed and submitted.
        wallet: the wallet with which to sign the transaction.
        client: the network client with which to submit the transaction.

    Returns:
        The response from the ledger.
    """
    transaction = safe_sign_transaction(transaction, wallet)
    return submit_transaction(transaction, client)


def safe_sign_transaction(transaction: Transaction, wallet: Wallet) -> Transaction:
    """
    Signs a transaction locally, without trusting external rippled nodes.

    Args:
        transaction: the transaction to be signed.
        wallet: the wallet with which to sign the transaction.

    Returns:
        The signed transaction blob.
    """
    # Increment the wallet sequence number, since we're about to use one.
    wallet.next_sequence_num += 1
    transaction_json = transaction_json_to_binary_codec_form(transaction.to_dict())
    transaction_json["SigningPubKey"] = wallet.pub_key
    serialized_for_signing = encode_for_signing(transaction_json)
    serialized_bytes = bytes.fromhex(serialized_for_signing)
    signature = sign(serialized_bytes, wallet.priv_key)
    transaction_json["TxnSignature"] = signature
    return cast(Transaction, Transaction.from_xrpl(transaction_json))


def submit_transaction(
    transaction: Transaction,
    client: Client,
) -> Response:
    """
    Submits a transaction to the ledger.

    Args:
        transaction: the Transaction to be submitted.
        client: the network client with which to submit the transaction.

    Returns:
        The response from the ledger.

    Raises:
        XRPLRequestFailureException: if the rippled API call fails.
    """
    transaction_json = transaction_json_to_binary_codec_form(transaction.to_dict())
    transaction_blob = encode(transaction_json)
    response = client.request(SubmitOnly(tx_blob=transaction_blob))
    if response.is_successful():
        return response

    result = cast(Dict[str, Any], response.result)
    raise XRPLRequestFailureException(result["error"], result["error_message"])


def transaction_json_to_binary_codec_form(dictionary: Dict[str, Any]) -> Dict[str, Any]:
    """
    Returns a new dictionary in which the keys have been formatted as CamelCase and
    standardized to be serialized by the binary codec.

    Args:
        dictionary: The dictionary to be reformatted.

    Returns:
        A new dictionary object that has been reformatted.
    """
    return {
        _key_to_tx_json(key): _value_to_tx_json(value)
        for (key, value) in dictionary.items()
    }


def _key_to_tx_json(key: str) -> str:
    snaked = "".join([word.capitalize() for word in key.split("_")])
    return re.sub(r"Id", r"ID", snaked)


def _value_to_tx_json(value: Any) -> Any:
    # IssuedCurrencyAmount is a special case and should not be snake cased
    if IssuedCurrencyAmount.is_dict_of_model(value):
        return {key: _value_to_tx_json(sub_value) for (key, sub_value) in value.items()}
    if isinstance(value, dict):
        return transaction_json_to_binary_codec_form(value)
    if isinstance(value, list):
        return [_value_to_tx_json(sub_value) for sub_value in value]
    return value
