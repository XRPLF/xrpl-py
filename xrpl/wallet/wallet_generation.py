"""Handles wallet generation from a faucet."""

from time import sleep

from requests import post

from xrpl import XRPLException
from xrpl.models.requests.accounts.account_info import AccountInfo
from xrpl.models.requests.fee import Fee
from xrpl.models.response import Response
from xrpl.network_clients import JsonRpcClient
from xrpl.wallet.main import Wallet

FAUCET_URL = "https://faucet.altnet.rippletest.net/accounts"


class XRPLFaucetException(XRPLException):
    """Faucet generation exception."""

    pass


# TODO: make this general for any type of network client
def generate_faucet_wallet(client: JsonRpcClient) -> Wallet:
    """
    Generates a random wallet and funds it using the XRPL Testnet Faucet.

    Args:
        client: the network client used to make network calls.

    Returns:
        A Wallet on the testnet that contains some amount of XRP.

    Raises:
        XRPLFaucetException: if an address could not be funded with the faucet.
    """
    timeout_seconds = 40
    wallet = Wallet.generate_seed_and_wallet()

    address = wallet.classic_address
    # The faucet *can* be flakey... by printing info about this it's easier to
    # understand if tests are actually failing, or if it was just a faucet failure.
    print("Attempting to fund address {}".format(address))
    # Balance prior to asking for more funds
    try:
        starting_balance = _get_balance(address, client)
    except KeyError:
        starting_balance = 0

    # Ask the faucet to send funds to the given address
    post(url=FAUCET_URL, json={"destination": address})
    # Wait for the faucet to fund our account or until timeout
    # Waits one second checks if balance has changed
    # If balance doesn't change it will attempt again until timeout_seconds
    for _ in range(timeout_seconds):
        sleep(1)
        try:
            current_balance = _get_balance(address, client)
        except KeyError:
            current_balance = 0
        # If our current balance has changed, then return
        if starting_balance != current_balance:
            print("Faucet fund successful.")
            wallet.next_sequence_num = get_next_valid_seq_number(
                wallet.classic_address, client
            )
            return wallet

    # Otherwise, timeout before balance updates
    raise XRPLFaucetException(
        "Unable to fund address with faucet after waiting {} seconds".format(
            timeout_seconds
        )
    )


def get_fee(client: JsonRpcClient) -> str:
    """
    Query the ledger for the current minimum transaction fee.

    Args:
        client: the network client used to make network calls.

    Returns:
        The minimum fee for transactions.
    """
    fee_request = Fee()
    response = client.request(fee_request)
    return str(response.result["drops"]["minimum_fee"])


def get_next_valid_seq_number(address: str, client: JsonRpcClient) -> int:
    """
    Query the ledger for the next available sequence number for an account.

    Args:
        address: the account to query.
        client: the network client used to make network calls.

    Returns:
        The next valid sequence number for the address.
    """
    account_info = _get_account_info(address, client)
    return account_info.result["account_data"]["Sequence"]


def _get_balance(address: str, client: JsonRpcClient) -> int:
    """Query the ledger for the balance of the given account."""
    account_info = _get_account_info(address, client)
    return int(account_info.result["account_data"]["Balance"])


def _get_account_info(address: str, client: JsonRpcClient) -> Response:
    """Query the ledger for account info of given address."""
    account_info_request = AccountInfo(
        account=address,
        ledger_index="validated",
    )
    return client.request(account_info_request)
