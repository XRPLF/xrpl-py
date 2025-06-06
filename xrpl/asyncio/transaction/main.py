"""High-level transaction methods with XRPL transactions."""

import math
from typing import Any, Dict, List, Optional, Union, cast

from typing_extensions import Final, TypeVar

from xrpl.asyncio.account import get_next_valid_seq_number
from xrpl.asyncio.clients import Client, XRPLRequestFailureException
from xrpl.asyncio.clients.client import get_network_id_and_build_version
from xrpl.asyncio.ledger import get_fee, get_latest_validated_ledger_sequence
from xrpl.constants import XRPLException
from xrpl.core.addresscodec import is_valid_xaddress, xaddress_to_classic_address
from xrpl.core.binarycodec import encode, encode_for_multisigning, encode_for_signing
from xrpl.core.keypairs.main import sign as keypairs_sign
from xrpl.models import (
    Batch,
    EscrowFinish,
    Response,
    ServerState,
    Simulate,
    SubmitOnly,
    Transaction,
    TransactionFlag,
)
from xrpl.models.transactions.transaction import (
    transaction_json_to_binary_codec_form as model_transaction_to_binary_codec,
)
from xrpl.models.transactions.types.transaction_type import TransactionType
from xrpl.utils import drops_to_xrp, xrp_to_drops
from xrpl.wallet import Wallet

_LEDGER_OFFSET: Final[int] = 20
# Sidechains are expected to have network IDs above this.
# Networks with ID above this restricted number are expected to specify an
# accurate NetworkID field in every transaction to that chain to prevent replay attacks.
# Mainnet and testnet are exceptions.
# More context: https://github.com/XRPLF/rippled/pull/4370
_RESTRICTED_NETWORKS = 1024
_REQUIRED_NETWORKID_VERSION = "1.11.0"

T = TypeVar("T", bound=Transaction, default=Transaction)


async def sign_and_submit(
    transaction: Transaction,
    client: Client,
    wallet: Wallet,
    autofill: bool = True,
    check_fee: bool = True,
) -> Response:
    """
    Signs a transaction (locally, without trusting external rippled nodes) and submits
    it to the XRPL.

    Args:
        transaction: the transaction to be signed and submitted.
        client: the network client with which to submit the transaction.
        wallet: the wallet with which to sign the transaction.
        autofill: whether to autofill the relevant fields. Defaults to True.
        check_fee: whether to check if the fee is higher than the expected transaction
            type fee. Defaults to True.

    Returns:
        The response from the ledger.
    """
    if autofill:
        transaction = await autofill_and_sign(transaction, client, wallet, check_fee)
    else:
        if check_fee:
            await _check_fee(transaction, client)
        transaction = sign(transaction, wallet)
    return await submit(transaction, client)


# Even though this is synchronous - this is here because it used to be async in
# xrpl-py 1.0, and we decided it wasn't worth breaking people's imports to move
# It to a central location as part of the xrpl-py 2.0 changes. It is aliased in
# The synchronous half of the library as well.
def sign(
    transaction: T,
    wallet: Wallet,
    multisign: bool = False,
) -> T:
    """
    Signs a transaction locally, without trusting external rippled nodes.

    Args:
        transaction: the transaction to be signed.
        wallet: the wallet with which to sign the transaction.
        multisign: whether to sign the transaction for a multisignature transaction.

    Returns:
        The signed transaction blob.
    """
    transaction_json = _prepare_transaction(transaction)
    if multisign:
        signature = keypairs_sign(
            bytes.fromhex(
                encode_for_multisigning(
                    transaction_json,
                    wallet.address,
                )
            ),
            wallet.private_key,
        )
        transaction_json["Signers"] = [
            {
                "Signer": {
                    "Account": wallet.address,
                    "TxnSignature": signature,
                    "SigningPubKey": wallet.public_key,
                }
            }
        ]
        return cast(T, Transaction.from_xrpl(transaction_json))

    transaction_json["SigningPubKey"] = wallet.public_key
    serialized_for_signing = encode_for_signing(transaction_json)
    serialized_bytes = bytes.fromhex(serialized_for_signing)
    signature = keypairs_sign(serialized_bytes, wallet.private_key)
    transaction_json["TxnSignature"] = signature
    return cast(T, Transaction.from_xrpl(transaction_json))


async def autofill_and_sign(
    transaction: T,
    client: Client,
    wallet: Wallet,
    check_fee: bool = True,
) -> T:
    """
    Autofills relevant fields. Then, signs a transaction locally, without trusting
    external rippled nodes.

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
    # will be auto-filled in autofill()
    if check_fee:
        await _check_fee(transaction, client)

    return sign(await autofill(transaction, client), wallet, multisign=False)


async def submit(
    transaction: Transaction,
    client: Client,
    *,
    fail_hard: bool = False,
) -> Response:
    """
    Submits a transaction to the ledger.

    Args:
        transaction: The Transaction to be submitted.
        client: The network client with which to submit the transaction.
        fail_hard: An optional boolean. If True, and the transaction fails for
            the initial server, do not retry or relay the transaction to other
            servers. Defaults to False.

    Returns:
        The response from the ledger.

    Raises:
        XRPLRequestFailureException: if the rippled API call fails.
    """
    transaction_blob = encode(transaction.to_xrpl())
    response = await client._request_impl(
        SubmitOnly(tx_blob=transaction_blob, fail_hard=fail_hard)
    )
    if response.is_successful():
        return response

    raise XRPLRequestFailureException(response.result)


async def simulate(
    transaction: Transaction,
    client: Client,
    *,
    binary: bool = False,
) -> Response:
    """
    Simulates a transaction without actually submitting it to the network.

    Args:
        transaction: The transaction to simulate.
        client: The network client with which to submit the transaction.
        binary: Whether the return data should be encoded in the XRPL's binary format.
            Defaults to False.

    Raises:
        XRPLRequestFailureException: If the transaction fails in the simulated scenario.

    Returns:
        The response from the ledger.
    """
    # autofill the network ID
    transaction_json = transaction.to_dict()
    await get_network_id_and_build_version(client)
    if "network_id" not in transaction_json and _tx_needs_networkID(client):
        transaction_json["network_id"] = client.network_id
    final_tx = Transaction.from_dict(transaction_json)

    # send the `simulate` request
    response = await client._request_impl(Simulate(transaction=final_tx, binary=binary))
    if response.is_successful():
        return response

    raise XRPLRequestFailureException(response.result)


def _prepare_transaction(transaction: Transaction) -> Dict[str, Any]:
    """
    Prepares a Transaction by converting it to a JSON-like dictionary, converting the
    field names to CamelCase. If a Client is provided, then it also autofills any
    relevant fields.

    Args:
        transaction: the Transaction to be prepared.

    Returns:
        A JSON-like dictionary that is ready to be signed.

    Raises:
        XRPLException: if both LastLedgerSequence and `ledger_offset` are provided, or
            if an address tag is provided that does not match the X-Address tag, or if
            attempting to directly sign a Batch inner transaction.
    """
    if transaction.has_flag(TransactionFlag.TF_INNER_BATCH_TXN):
        raise XRPLException("Cannot directly sign a batch inner transaction.")

    transaction_json = transaction.to_xrpl()

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


async def autofill(
    transaction: T, client: Client, signers_count: Optional[int] = None
) -> T:
    """
    Autofills fields in a transaction. This will set all autofill-able fields according
    to the current state of the server this Client is connected to. For Batch
    transactions, it will also handle autofilling inner transactions. It also converts
    all X-Addresses to classic addresses.

    Args:
        transaction: the transaction to be signed.
        client: a network client.
        signers_count: the expected number of signers for this transaction.
            Only used for multisigned transactions.

    Raises:
        XRPLException: If a field is pre-filled out incorrectly.

    Returns:
        The autofilled transaction.
    """
    transaction_json = transaction.to_dict()
    await get_network_id_and_build_version(client)
    if "network_id" not in transaction_json and _tx_needs_networkID(client):
        transaction_json["network_id"] = client.network_id
    if "sequence" not in transaction_json:
        if "ticket_sequence" in transaction_json:
            sequence = 0
        else:
            sequence = await get_next_valid_seq_number(
                transaction_json["account"], client
            )
        transaction_json["sequence"] = sequence
    if "fee" not in transaction_json:
        transaction_json["fee"] = await _calculate_fee_per_transaction_type(
            transaction, client, signers_count
        )
    if "last_ledger_sequence" not in transaction_json:
        ledger_sequence = await get_latest_validated_ledger_sequence(client)
        transaction_json["last_ledger_sequence"] = ledger_sequence + _LEDGER_OFFSET
    if transaction.transaction_type == TransactionType.BATCH:
        inner_txs = await _autofill_batch(client, transaction_json)
        transaction_json["raw_transactions"] = inner_txs
    return cast(T, Transaction.from_dict(transaction_json))


def _tx_needs_networkID(client: Client) -> bool:
    """
    Determines whether the transactions required network ID to be valid.
    Transaction needs networkID if later than restricted ID and either
        the network is hooks testnet or build version is >= 1.11.0.
    More context: https://github.com/XRPLF/rippled/pull/4370

    Args:
        client (Client): The network client to use to send the request.

    Returns:
        bool: whether the transactions required network ID to be valid
    """
    if client.network_id is not None and client.network_id > _RESTRICTED_NETWORKS:
        if client.build_version and _is_not_later_rippled_version(
            _REQUIRED_NETWORKID_VERSION, client.build_version
        ):
            return True
    return False


def _is_not_later_rippled_version(source: str, target: str) -> bool:
    """
    Determines whether the source version is not a later release than the
        target version.

    Args:
        source: the source rippled version.
        target: the target rippled version.

    Returns:
        bool: true if source is earlier, false otherwise.
    """
    if source == target:
        return True
    source_decomp = source.split(".")
    target_decomp = target.split(".")
    source_major, source_minor = int(source_decomp[0]), int(source_decomp[1])
    target_major, target_minor = int(target_decomp[0]), int(target_decomp[1])

    # Compare major version
    if source_major != target_major:
        return source_major < target_major

    # Compare minor version
    if source_minor != target_minor:
        return source_minor < target_minor

    source_patch = source_decomp[2].split("-")
    target_patch = target_decomp[2].split("-")
    source_patch_version = int(source_patch[0])
    target_patch_version = int(target_patch[0])

    # Compare patch version
    if source_patch_version != target_patch_version:
        return source_patch_version < target_patch_version

    # Compare release version
    if len(source_patch) != len(target_patch):
        return len(source_patch) > len(target_patch)

    if len(source_patch) == 2:
        # Compare release types
        if not source_patch[1][0].startswith(target_patch[1][0]):
            return source_patch[1] < target_patch[1]
        # Compare beta versions
        if source_patch[1].startswith("b"):
            return int(source_patch[1][1:]) < int(target_patch[1][1:])
        # Compare rc versions
        return int(source_patch[1][2:]) < int(target_patch[1][2:])
    return False


def _validate_account_xaddress(
    json: Dict[str, Any], account_field: str, tag_field: str
) -> None:
    """
    Mutates JSON-like dictionary so the X-Address in the account field is the classic
    address, and the tag is in the tag field.

    Args:
        json: JSON-like dictionary with transaction data or similar
        account_field: the field of `json` that may contain an X-Address
        tag_field: the field of `json` that may contain a source or destination tag

    Raises:
        XRPLException: if both an X-Address containing a tag and a tag field are
            provided and they do not match.
    """
    if is_valid_xaddress(json[account_field]):
        account, tag, _ = xaddress_to_classic_address(json[account_field])
        json[account_field] = account
        if tag_field in json and json[tag_field] != tag:
            raise XRPLException(f"{tag_field} value does not match X-Address tag")
        json[tag_field] = tag


def _convert_to_classic_address(json: Dict[str, Any], field: str) -> None:
    """
    Mutates JSON-like dictionary to convert the given field from an X-Address (if
    applicable) to a classic address.

    Args:
        json: JSON-like dictionary with transaction data or similar
        field: the field in `json` that may contain an X-Address
    """
    if field in json and is_valid_xaddress(json[field]):
        json[field] = xaddress_to_classic_address(json[field])[0]


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


async def _check_fee(
    transaction: Transaction,
    client: Client,
    signers_count: Optional[int] = None,
) -> None:
    """
    Checks if the Transaction fee is higher than the expected Transaction type fee.

    Args:
        transaction: The transaction to check.
        client: Client instance to use to look up network load
        signers_count: the expected number of signers for this transaction.
            Only used for multisigned transactions.

    Raises:
        XRPLException: if the transaction fee is higher than the expected fee.
    """
    expected_fee = max(
        int(xrp_to_drops(0.1)),  # a fee that is obviously too high
        int(
            await _calculate_fee_per_transaction_type(
                transaction, client, signers_count
            )
        ),
    )

    if transaction.fee and int(transaction.fee) > expected_fee:
        raise XRPLException(
            f"Fee value: {str(drops_to_xrp(transaction.fee))} XRP is likely entered "
            "incorrectly, since it is much larger than the typical XRP transaction "
            "cost. If this is intentional, use `check_fee=False`."
        )


async def _calculate_fee_per_transaction_type(
    transaction: Transaction,
    client: Client,
    signers_count: Optional[int] = None,
) -> str:
    """
    Calculate the total fee in drops for a transaction based on:
    - the network fee
    - the transaction condition

    https://xrpl.org/transaction-cost.html#special-transaction-costs

    Args:
        transaction: the Transaction to be submitted.
        client: the network client with which to submit the transaction.
        signers_count: the expected number of signers for this transaction.
            Only used for multisigned transactions and multi-account/multi-signed Batch
            transactions.

    Returns:
        The expected Transaction fee in drops
    """
    # Reference Transaction (Most transactions)

    net_fee = int(
        await get_fee(client)
    )  # Latest data is found in FeeSettings ledger-object's BaseFee field.

    base_fee = net_fee

    # EscrowFinish Transaction with Fulfillment
    # https://xrpl.org/escrowfinish.html#escrowfinish-fields
    if transaction.transaction_type == TransactionType.ESCROW_FINISH:
        escrow_finish = cast(EscrowFinish, transaction)
        if escrow_finish.fulfillment is not None:
            fulfillment_bytes = escrow_finish.fulfillment.encode("ascii")
            # BaseFee × (33 + (Fulfillment size in bytes / 16))
            base_fee = math.ceil(net_fee * (33 + (len(fulfillment_bytes) / 16)))

    # AccountDelete Transaction
    elif transaction.transaction_type in (
        TransactionType.ACCOUNT_DELETE,
        TransactionType.AMM_CREATE,
    ):
        base_fee = await _fetch_owner_reserve_fee(client)

    elif transaction.transaction_type == TransactionType.BATCH:
        batch = cast(Batch, transaction)
        base_fee = base_fee * 2 + sum(
            [
                int(await _calculate_fee_per_transaction_type(raw_txn, client))
                for raw_txn in batch.raw_transactions
            ]
        )

    # Multi-signed/Multi-Account Batch Transactions
    # BaseFee × (1 + Number of Signatures Provided)
    if signers_count is not None and signers_count > 0:
        base_fee += net_fee * signers_count
    # Round Up base_fee and return it as a String
    return str(math.ceil(base_fee))


async def _fetch_owner_reserve_fee(client: Client) -> int:
    server_state = await client._request_impl(ServerState())
    fee = server_state.result["state"]["validated_ledger"]["reserve_inc"]
    return int(fee)


async def _autofill_batch(
    client: Client, transaction_dict: Dict[str, Any]
) -> List[Dict[str, Any]]:
    transaction = Batch.from_dict(transaction_dict)
    assert transaction.sequence is not None
    account_sequences: Dict[str, int] = {transaction.account: transaction.sequence + 1}
    inner_txs: List[Dict[str, Any]] = []

    for raw_txn in transaction.raw_transactions:
        raw_txn_dict = raw_txn.to_dict()

        if raw_txn.transaction_type == TransactionType.BATCH:
            raise XRPLException(
                "Cannot have a Batch transaction inside a Batch transaction."
            )
        if raw_txn.sequence is None and raw_txn.ticket_sequence is None:
            # autofill sequence
            if raw_txn.account in account_sequences:
                raw_txn_dict["sequence"] = account_sequences[raw_txn.account]
                account_sequences[raw_txn.account] += 1
            else:
                sequence = await get_next_valid_seq_number(raw_txn.account, client)
                account_sequences[raw_txn.account] = sequence + 1
                raw_txn_dict["sequence"] = sequence

        if raw_txn.is_signed():
            raise XRPLException("Inner Batch transactions must not be signed.")

        # validate fields that are supposed to be empty/zeroed
        def _validate_field(field_name: str, expected_value: Union[str, None]) -> None:
            if field_name not in raw_txn_dict:
                raw_txn_dict[field_name] = expected_value
            elif raw_txn_dict[field_name] != expected_value:
                raise XRPLException(
                    f"Must have a `{field_name}` of {repr(expected_value)} in an "
                    "inner Batch transaction."
                )

        _validate_field("fee", "0")
        _validate_field("signing_pub_key", "")
        _validate_field("txn_signature", None)

        if raw_txn.txn_signature is not None:
            raise XRPLException(
                "Must not have a `txn_signature` field in an inner Batch transaction."
            )
        if raw_txn.signers is not None:
            raise XRPLException(
                "Must not have a `signers` field in an inner Batch transaction."
            )
        if raw_txn.network_id is None and _tx_needs_networkID(client):
            raw_txn_dict["network_id"] = client.network_id
        if raw_txn.last_ledger_sequence is not None:
            raise XRPLException(
                "Must not have a `last_ledger_sequence` field in an inner Batch "
                "transaction."
            )

        inner_txs.append(raw_txn_dict)

    return inner_txs
