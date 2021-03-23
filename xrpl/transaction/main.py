"""High-level transaction methods with XRPL transactions."""
import re
from typing import Any, Dict, Optional

from xrpl import XRPLException
from xrpl.account import get_next_valid_seq_number
from xrpl.clients import Client
from xrpl.core.addresscodec import is_valid_xaddress, xaddress_to_classic_address
from xrpl.core.binarycodec import encode, encode_for_signing
from xrpl.core.keypairs.main import sign
from xrpl.ledger import get_fee
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
    tx_blob = safe_sign_transaction(transaction, wallet)
    return submit_transaction_blob(tx_blob, client)


def safe_sign_transaction(transaction: Transaction, wallet: Wallet) -> str:
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
    return encode(transaction_json)


def submit_transaction_blob(
    transaction_blob: str,
    client: Client,
) -> Response:
    """
    Submits a transaction blob to the ledger.

    Args:
        transaction_blob: the transaction blob to be submitted.
        client: the network client with which to submit the transaction.

    Returns:
        The response from the ledger.
    """
    submit_request = SubmitOnly(tx_blob=transaction_blob)
    return client.request(submit_request)


def prepare_transaction(
    transaction: Transaction,
    wallet: Wallet,
    client: Client,
    ledger_offset: Optional[int] = None,
) -> Dict[str, Any]:
    """
    Prepares a Transaction by converting it to a JSON-like dictionary, filling in all
    the auto-fill fields, and converting the field names to CamelCase.

    Args:
        transaction: the Transaction to be prepared.
        wallet: the wallet that will be used for signing.
        client: the API client used for any network calls.
        ledger_offset: If LastLedgerSequence is not provided in the transaction, then
            this value is used as an offset from the current sequence number for the
            LastLedgerSequence.

    Returns:
        A JSON-like dictionary that is ready to be signed.

    Raises:
        XRPLException: if both LastLedgerSequence and `ledger_offset` are provided, or
            if an address tag is provided that does not match the X-Address tag.
    """
    wallet.next_sequence_num += 1
    transaction_json = transaction_json_to_binary_codec_form(transaction.to_dict())
    transaction_json["SigningPubKey"] = wallet.pub_key

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

    sequence = None
    if "Sequence" not in transaction_json:
        sequence = get_next_valid_seq_number(transaction_json["Account"], client)
        transaction_json["Sequence"] = sequence
    if "Fee" not in transaction_json:
        transaction_json["Fee"] = get_fee(client)

    if "LastLedgerSequence" in transaction_json and ledger_offset is not None:
        raise XRPLException(
            "Cannot have LastLedgerSequence defined in transaction and have a ledger "
            "offset parameter."
        )
    if "LastLedgerSequence" not in transaction_json and ledger_offset is not None:
        if sequence is None:
            sequence = get_next_valid_seq_number(transaction.account, client)
        transaction_json["LastLedgerSequence"] = sequence + ledger_offset

    return transaction_json


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
