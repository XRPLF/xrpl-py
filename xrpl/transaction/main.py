"""High-level transaction methods with XRPL transactions."""
import re
from typing import Any, Dict, cast

from typing_extensions import Final

from xrpl.account import get_next_valid_seq_number
from xrpl.clients import Client, XRPLRequestFailureException
from xrpl.constants import XRPLException
from xrpl.core.addresscodec import is_valid_xaddress, xaddress_to_classic_address
from xrpl.core.binarycodec import encode, encode_for_signing
from xrpl.core.keypairs.main import sign
from xrpl.ledger import get_fee, get_latest_validated_ledger_sequence
from xrpl.models.amounts import IssuedCurrencyAmount
from xrpl.models.requests import SubmitOnly
from xrpl.models.response import Response
from xrpl.models.transactions.transaction import Transaction
from xrpl.wallet.main import Wallet

_LEDGER_OFFSET: Final[int] = 20


def safe_sign_and_submit_transaction(
    transaction: Transaction, wallet: Wallet, client: Client, autofill: bool = True
) -> Response:
    """
    Signs a transaction (locally, without trusting external rippled nodes) and submits
    it to the XRPL.

    Args:
        transaction: the transaction to be signed and submitted.
        wallet: the wallet with which to sign the transaction.
        client: the network client with which to submit the transaction.
        autofill: whether to autofill the relevant fields. Defaults to True.

    Returns:
        The response from the ledger.
    """
    if autofill:
        transaction = safe_sign_and_autofill_transaction(transaction, wallet, client)
    else:
        transaction = safe_sign_transaction(transaction, wallet)
    return submit_transaction(transaction, client)


def safe_sign_transaction(
    transaction: Transaction,
    wallet: Wallet,
) -> Transaction:
    """
    Signs a transaction locally, without trusting external rippled nodes.

    Args:
        transaction: the transaction to be signed.
        wallet: the wallet with which to sign the transaction.

    Returns:
        The signed transaction blob.
    """
    transaction_json = _prepare_transaction(transaction, wallet)
    serialized_for_signing = encode_for_signing(transaction_json)
    serialized_bytes = bytes.fromhex(serialized_for_signing)
    signature = sign(serialized_bytes, wallet.private_key)
    transaction_json["TxnSignature"] = signature
    return cast(Transaction, Transaction.from_xrpl(transaction_json))


def safe_sign_and_autofill_transaction(
    transaction: Transaction, wallet: Wallet, client: Client
) -> Transaction:
    """
    Signs a transaction locally, without trusting external rippled nodes. Autofills
    relevant fields.

    Args:
        transaction: the transaction to be signed.
        wallet: the wallet with which to sign the transaction.
        client: a network client.

    Returns:
        The signed transaction.
    """
    return safe_sign_transaction(_autofill_transaction(transaction, client), wallet)


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
    raise XRPLRequestFailureException(result)


def _prepare_transaction(
    transaction: Transaction,
    wallet: Wallet,
) -> Dict[str, Any]:
    """
    Prepares a Transaction by converting it to a JSON-like dictionary, converting the
    field names to CamelCase. If a Client is provided, then it also autofills any
    relevant fields.

    Args:
        transaction: the Transaction to be prepared.
        wallet: the wallet that will be used for signing.

    Returns:
        A JSON-like dictionary that is ready to be signed.

    Raises:
        XRPLException: if both LastLedgerSequence and `ledger_offset` are provided, or
            if an address tag is provided that does not match the X-Address tag.
    """
    transaction_json = transaction_json_to_binary_codec_form(transaction.to_dict())
    transaction_json["SigningPubKey"] = wallet.public_key

    _validate_account_xaddress(transaction_json, "Account", "SourceTag")
    if "Destination" in transaction_json:
        _validate_account_xaddress(transaction_json, "Destination", "DestinationTag")

    # DepositPreauth
    _convert_to_classic_address(transaction_json, "Authorize")
    _convert_to_classic_address(transaction_json, "Unauthorize")
    # EscrowCancel, EscrowFinish
    _convert_to_classic_address(transaction_json, "Owner")
    # SetRegularKey
    _convert_to_classic_address(transaction_json, "RegularKey")

    return transaction_json


def _autofill_transaction(transaction: Transaction, client: Client) -> Transaction:
    transaction_json = transaction.to_dict()
    if "sequence" not in transaction_json:
        sequence = get_next_valid_seq_number(transaction_json["account"], client)
        transaction_json["sequence"] = sequence
    if "fee" not in transaction_json:
        transaction_json["fee"] = get_fee(client)
    if "last_ledger_sequence" not in transaction_json:
        ledger_sequence = get_latest_validated_ledger_sequence(client)
        transaction_json["last_ledger_sequence"] = ledger_sequence + _LEDGER_OFFSET
    return Transaction.from_dict(transaction_json)


def _validate_account_xaddress(
    json: Dict[str, Any], account_field: str, tag_field: str
) -> None:
    """
    Mutates JSON-like dictionary so the X-Address in the account field is the classic
    address, and the tag is in the tag field.
    """
    if is_valid_xaddress(json[account_field]):
        account, tag, _ = xaddress_to_classic_address(json[account_field])
        json[account_field] = account
        if json[tag_field] and json[tag_field] != tag:
            raise XRPLException(f"{tag_field} value does not match X-Address tag")
        json[tag_field] = tag


def _convert_to_classic_address(json: Dict[str, Any], field: str) -> None:
    """
    Mutates JSON-like dictionary to convert the given field from an X-address (if
    applicable) to a classic address.
    """
    if field in json and is_valid_xaddress(json[field]):
        json[field] = xaddress_to_classic_address(json[field])


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
