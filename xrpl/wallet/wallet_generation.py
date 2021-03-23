"""Handles wallet generation from a faucet."""

from time import sleep

from requests import post

from xrpl import XRPLException
from xrpl.account import get_balance, get_next_valid_seq_number
from xrpl.clients import Client, XRPLRequestFailureException
from xrpl.wallet.main import Wallet

FAUCET_URL = "https://faucet.altnet.rippletest.net/accounts"


class XRPLFaucetException(XRPLException):
    """Faucet generation exception."""

    pass


def generate_faucet_wallet(client: Client, debug: bool = False) -> Wallet:
    """
    Generates a random wallet and funds it using the XRPL Testnet Faucet.

    Args:
        client: the network client used to make network calls.
        debug: Whether to print debug information as it creates the wallet.

    Returns:
        A Wallet on the testnet that contains some amount of XRP.

    Raises:
        XRPLFaucetException: if an address could not be funded with the faucet.
    """
    timeout_seconds = 40
    wallet = Wallet.create()

    address = wallet.classic_address
    # The faucet *can* be flakey... by printing info about this it's easier to
    # understand if tests are actually failing, or if it was just a faucet failure.
    if debug:
        print("Attempting to fund address {}".format(address))
    # Balance prior to asking for more funds
    try:
        starting_balance = get_balance(address, client)
    except XRPLRequestFailureException:
        starting_balance = 0

    # Ask the faucet to send funds to the given address
    post(url=FAUCET_URL, json={"destination": address})
    # Wait for the faucet to fund our account or until timeout
    # Waits one second checks if balance has changed
    # If balance doesn't change it will attempt again until timeout_seconds
    for _ in range(timeout_seconds):
        sleep(1)
        try:
            current_balance = get_balance(address, client)
        except XRPLRequestFailureException:
            current_balance = 0
        # If our current balance has changed, then return
        if starting_balance != current_balance:
            if debug:
                print("Faucet fund successful.")
            try:
                wallet.next_sequence_num = get_next_valid_seq_number(address, client)
            except XRPLRequestFailureException as e:
                if e.error_code == "actNotFound":
                    # try again after waiting a bit
                    sleep(1)
                    wallet.next_sequence_num = get_next_valid_seq_number(
                        address, client
                    )
            return wallet

    # Otherwise, timeout before balance updates
    raise XRPLFaucetException(
        "Unable to fund address with faucet after waiting {} seconds".format(
            timeout_seconds
        )
    )
