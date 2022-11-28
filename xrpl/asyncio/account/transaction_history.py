"""High-level methods to obtain information about account transaction history."""
from typing import Any, Dict, List, cast

from deprecated.sphinx import deprecated

from xrpl.asyncio.clients import Client, XRPLRequestFailureException
from xrpl.core.addresscodec import is_valid_xaddress, xaddress_to_classic_address
from xrpl.models.requests import AccountTx
from xrpl.models.response import Response


async def get_latest_transaction(account: str, client: Client) -> Response:
    """
    Fetches the most recent transaction on the ledger associated with an account.

    Args:
        account: the account to query.
        client: the network client used to communicate with a rippled node.

    Returns:
        The Response object containing the transaction info.

    Raises:
        XRPLRequestFailureException: if the transaction fails.
    """
    # max == -1 means that it's the most recent validated ledger version
    if is_valid_xaddress(account):
        account, _, _ = xaddress_to_classic_address(account)
    response = await client._request_impl(
        AccountTx(account=account, ledger_index_max=-1, limit=1)
    )
    if not response.is_successful():
        raise XRPLRequestFailureException(response.result)
    return response


@deprecated(
    reason="Sending an AccountTx request directly allows you to page through all "
    "results and is just as easy to use.",
    version="1.6.0",
)
async def get_account_transactions(
    address: str,
    client: Client,
) -> List[Dict[str, Any]]:
    """
    Query the ledger for a list of transactions that involved a given account.
    To access more than just the first page of results, use the :class:`AccountTx`
    request directly.

    Args:
        address: the account to query.
        client: the network client used to make network calls.

    Returns:
        The most recent transaction history for the address. For the full history,
        page through the :class:`AccountTx` request directly.

    Raises:
        XRPLRequestFailureException: if the transaction fails.
    """
    if is_valid_xaddress(address):
        address, _, _ = xaddress_to_classic_address(address)
    request = AccountTx(account=address)
    response = await client._request_impl(request)
    if not response.is_successful():
        raise XRPLRequestFailureException(response.result)
    return cast(List[Dict[str, Any]], response.result["transactions"])


@deprecated(
    reason="Sending an AccountTx request directly and filtering for payments allows "
    "you to page through all results and is just as easy to use.",
    version="1.8.0",
)
async def get_account_payment_transactions(
    address: str,
    client: Client,
) -> List[Dict[str, Any]]:
    """
    Query the ledger for a list of payment transactions that involved a given account.
    To access more than just the first page of results, use the :class:`AccountTx`
    request directly then filter for transactions with a "Payment" TransactionType.

    Args:
        address: the account to query.
        client: the network client used to make network calls.

    Returns:
        The first page of payment transaction history for the address. For the full
        history, page through the :class:`AccountTx` request directly.
    """
    all_transactions = await get_account_transactions(address, client)
    return [tx for tx in all_transactions if tx["tx"]["TransactionType"] == "Payment"]
