"""High-level transaction methods with XRPL transactions."""
import math
from typing import Any, Dict, Optional, cast

from typing_extensions import Final

from xrpl.asyncio.account import get_next_valid_seq_number
from xrpl.asyncio.clients import Client, XRPLRequestFailureException
from xrpl.asyncio.ledger import get_fee, get_latest_validated_ledger_sequence
from xrpl.constants import XRPLException
from xrpl.core.addresscodec import is_valid_xaddress, xaddress_to_classic_address
from xrpl.core.binarycodec import encode, encode_for_signing
from xrpl.core.keypairs.main import sign
from xrpl.models.requests import SubmitOnly
from xrpl.models.response import Response
from xrpl.models.transactions.escrow_finish import EscrowFinish
from xrpl.models.transactions.transaction import Transaction
from xrpl.models.transactions.transaction import (
    transaction_json_to_binary_codec_form as model_transaction_to_binary_codec,
)
from xrpl.models.transactions.types.transaction_type import TransactionType
from xrpl.utils import drops_to_xrp
from xrpl.wallet.main import Wallet

_LEDGER_OFFSET: Final[int] = 20
_ACCOUNT_DELETE_FEE: Final[int] = 5000000


async def safe_sign_and_submit_transaction(
    transaction: Transaction,
    wallet: Wallet,
    client: Client,
    autofill: bool = True,
    check_fee: bool = True,
) -> Response:
    """
    Signs a transaction (locally, without trusting external rippled nodes) and submits
    it to the XRPL.

    Args:
        transaction: the transaction to be signed and submitted.
        wallet: the wallet with which to sign the transaction.
        client: the network client with which to submit the transaction.
        autofill: whether to autofill the relevant fields. Defaults to True.
        check_fee: whether to check if the fee is higher than the expected transaction
            type fee. Defaults to True.

    Returns:
        The response from the ledger.
    """
    if autofill:
        transaction = await safe_sign_and_autofill_transaction(
            transaction, wallet, client, check_fee
        )
    else:
        transaction = await safe_sign_transaction(transaction, wallet, check_fee)
    return await submit_transaction(transaction, client)


async def safe_sign_transaction(
    transaction: Transaction,
    wallet: Wallet,
    check_fee: bool = True,
) -> Transaction:
    """
    Signs a transaction locally, without trusting external rippled nodes.

    Args:
        transaction: the transaction to be signed.
        wallet: the wallet with which to sign the transaction.
        check_fee: whether to check if the fee is higher than the expected transaction
            type fee. Defaults to True.

    Returns:
        The signed transaction blob.
    """
    if check_fee:
        await _check_fee(transaction)
    transaction_json = _prepare_transaction(transaction, wallet)
    serialized_for_signing = encode_for_signing(transaction_json)
    serialized_bytes = bytes.fromhex(serialized_for_signing)
    signature = sign(serialized_bytes, wallet.private_key)
    transaction_json["TxnSignature"] = signature
    return cast(Transaction, Transaction.from_xrpl(transaction_json))


async def safe_sign_and_autofill_transaction(
    transaction: Transaction,
    wallet: Wallet,
    client: Client,
    check_fee: bool = True,
) -> Transaction:
    """
    Signs a transaction locally, without trusting external rippled nodes. Autofills
    relevant fields.

    Args:
        transaction: the transaction to be signed.
        wallet: the wallet with which to sign the transaction.
        client: a network client.
        check_fee: whether to check if the fee is higher than the expected transaction
            type fee. Defaults to True.

    Returns:
        The signed transaction.
    """
    # We do the transaction fee check here as we have the Client available.
    # The fee check will be done if transaction.fee exists. Otherwise the fee
    # will be auto-filled in _autofill_transaction()
    if check_fee:
        await _check_fee(transaction, client)

    return await safe_sign_transaction(
        await _autofill_transaction(transaction, client), wallet, False
    )


async def submit_transaction(
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
    transaction_blob = encode(transaction.to_xrpl())
    response = await client.request_impl(SubmitOnly(tx_blob=transaction_blob))
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
    transaction_json = transaction.to_xrpl()
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


async def _autofill_transaction(
    transaction: Transaction, client: Client
) -> Transaction:
    transaction_json = transaction.to_dict()
    if "sequence" not in transaction_json:
        sequence = await get_next_valid_seq_number(transaction_json["account"], client)
        transaction_json["sequence"] = sequence
    if "fee" not in transaction_json:
        transaction_json["fee"] = await _calculate_fee_per_transaction_type(
            transaction, client
        )
    if "last_ledger_sequence" not in transaction_json:
        ledger_sequence = await get_latest_validated_ledger_sequence(client)
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
    return model_transaction_to_binary_codec(dictionary)


async def _check_fee(transaction: Transaction, client: Optional[Client] = None) -> None:
    """Checks if the Transaction fee is lower than the expected Transaction type fee"""
    # Calculate the expected fee from the network load and transaction type
    expected_fee = await _calculate_fee_per_transaction_type(transaction, client)

    if transaction.fee and int(transaction.fee) > int(expected_fee):
        raise XRPLException(
            "Fee value: "
            + str(drops_to_xrp(transaction.fee))
            + " XRP exceeds the "
            + str(drops_to_xrp(expected_fee))
            + " maximum XRP fee limit for "
            + transaction.transaction_type
            + " transaction"
        )


async def _calculate_fee_per_transaction_type(
    transaction: Transaction, client: Optional[Client] = None
) -> str:
    """
    Calculate the total fee in drops for a transaction based on:
    - the network fee
    - the transaction condition

    https://xrpl.org/transaction-cost.html#special-transaction-costs

    Args:
        transaction: the Transaction to be submitted.
        client: the network client with which to submit the transaction.

    Returns:
        The expected Transaction fee in drops
    """
    # Reference Transaction (Most transactions)
    if client is None:
        net_fee = 10  # 10 drops
    else:
        net_fee = int(await get_fee(client))  # Usually 0.00001 XRP (10 drops)

    base_fee = net_fee

    # EscrowFinish Transaction with Fulfillment
    # https://xrpl.org/escrowfinish.html#escrowfinish-fields
    if transaction.transaction_type == TransactionType.ESCROW_FINISH:
        escrow_finish = cast(EscrowFinish, transaction)
        if escrow_finish.fulfillment is not None:
            fulfillment_bytes = escrow_finish.fulfillment.encode("ascii")
            # 10 drops × (33 + (Fulfillment size in bytes / 16))
            base_fee = math.ceil(net_fee * (33 + (len(fulfillment_bytes) / 16)))

    # AccountDelete Transaction
    if transaction.transaction_type == TransactionType.ACCOUNT_DELETE:
        base_fee = _ACCOUNT_DELETE_FEE

    # Multi-signed Transaction
    # 10 drops × (1 + Number of Signatures Provided)
    if transaction.signers and len(transaction.signers) > 0:
        base_fee = net_fee * (1 + len(transaction.signers)) + base_fee

    # Round Up base_fee and return it as a String
    return str(math.ceil(base_fee))
