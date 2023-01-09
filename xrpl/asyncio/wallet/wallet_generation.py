"""Handles wallet generation from a faucet."""
import asyncio
from typing import Optional

import httpx
from typing_extensions import Final

from xrpl.asyncio.account import get_balance, get_next_valid_seq_number
from xrpl.asyncio.clients import Client, XRPLRequestFailureException
from xrpl.constants import XRPLException
from xrpl.wallet.main import Wallet

_TEST_FAUCET_URL: Final[str] = "https://faucet.altnet.rippletest.net/accounts"
_DEV_FAUCET_URL: Final[str] = "https://faucet.devnet.rippletest.net/accounts"
_AMM_DEV_FAUCET_URL: Final[str] = "https://ammfaucet.devnet.rippletest.net/accounts"
# TODO: Remove this once nft devnet is decomissioned
_NFT_DEV_FAUCET_URL: Final[str] = "https://faucet-nft.ripple.com/accounts"
_ICV2_FAUCET_URL: Final[str] = "https://icv2.faucet.transia.co/accounts"
_HOOKS_V2_TEST_FAUCET_URL: Final[
    str
] = "https://hooks-testnet-v2.xrpl-labs.com/accounts"

_TIMEOUT_SECONDS: Final[int] = 40


class XRPLFaucetException(XRPLException):
    """Faucet generation exception."""

    pass


async def generate_faucet_wallet(
    client: Client,
    wallet: Optional[Wallet] = None,
    debug: bool = False,
    faucet_host: Optional[str] = None,
) -> Wallet:
    """
    Generates a random wallet and funds it using the XRPL Testnet Faucet.

    Args:
        client: the network client used to make network calls.
        wallet: the wallet to fund. If omitted or `None`, a new wallet is created.
        debug: Whether to print debug information as it creates the wallet.
        faucet_host: A custom host to use for funding a wallet. In environments other
            than devnet and testnet, this parameter is required.

    Returns:
        A Wallet on the testnet that contains some amount of XRP.

    Raises:
        XRPLFaucetException: if an address could not be funded with the faucet.
        XRPLRequestFailureException: if a request to the ledger fails.
        requests.exceptions.HTTPError: if the request to the faucet fails.

    .. # noqa: DAR402 exception raised in private method
    """
    faucet_url = get_faucet_url(client.url, faucet_host)

    if wallet is None:
        wallet = Wallet.create()

    address = wallet.classic_address
    # The faucet *can* be flakey... by printing info about this it's easier to
    # understand if tests are actually failing, or if it was just a faucet failure.
    if debug:
        print("Attempting to fund address {}".format(address))
    # Balance prior to asking for more funds
    starting_balance = await _check_wallet_balance(address, client)

    # Ask the faucet to send funds to the given address
    await _request_funding(faucet_url, address)
    # Wait for the faucet to fund our account or until timeout
    # Waits one second checks if balance has changed
    # If balance doesn't change it will attempt again until _TIMEOUT_SECONDS
    is_funded = False
    for _ in range(_TIMEOUT_SECONDS):
        await asyncio.sleep(1)
        if not is_funded:  # faucet transaction hasn't been validated yet
            current_balance = await _check_wallet_balance(address, client)
            # If our current balance has changed, then the account has been funded
            if current_balance > starting_balance:
                if debug:
                    print("Faucet fund successful.")
                is_funded = True
        else:  # wallet has been funded, now the ledger needs to know the account exists
            next_seq_num = await _try_to_get_next_seq(address, client)
            if next_seq_num is not None:
                wallet.sequence = next_seq_num
                return wallet

    raise XRPLFaucetException(
        "Unable to fund address with faucet after waiting {} seconds".format(
            _TIMEOUT_SECONDS
        )
    )


def get_faucet_url(url: str, faucet_host: Optional[str] = None) -> str:
    """
    Returns the URL of the faucet that should be used, based on whether the URL is from
    a testnet or devnet client.

    Args:
        url: The URL that the client is using to access the ledger.
        faucet_host: A custom host to use for funding a wallet.

    Returns:
        The URL of the matching faucet.

    Raises:
        XRPLFaucetException: if the provided URL is not for the testnet or devnet.
    """
    if faucet_host is not None:
        return f"https://{faucet_host}/accounts"
    if "hooks-testnet-v2" in url:  # hooks v2 testnet
        return _HOOKS_V2_TEST_FAUCET_URL
    if "altnet" in url or "testnet" in url:  # testnet
        return _TEST_FAUCET_URL
    if "amm" in url:  # amm devnet
        return _AMM_DEV_FAUCET_URL
    if "devnet" in url:  # devnet
        return _DEV_FAUCET_URL
    # TODO: Remove this once the network is fully decommissioned
    if "xls20-sandbox" in url:  # nft devnet
        return _NFT_DEV_FAUCET_URL
    if "icv2" in url:  # icv2
        return _ICV2_FAUCET_URL
    raise XRPLFaucetException(
        "Cannot fund an account with a client that is not on the testnet or devnet."
    )


async def _check_wallet_balance(address: str, client: Client) -> int:
    try:
        return await get_balance(address, client)
    except XRPLRequestFailureException as e:
        if e.error == "actNotFound":  # transaction has not gone through
            return 0
        # some other error
        raise


async def _request_funding(url: str, address: str) -> None:
    async with httpx.AsyncClient() as http_client:
        response = await http_client.post(url=url, json={"destination": address})
    if not response.status_code == httpx.codes.OK:
        response.raise_for_status()


async def _try_to_get_next_seq(address: str, client: Client) -> Optional[int]:
    try:
        return await get_next_valid_seq_number(address, client)
    except XRPLRequestFailureException as e:
        if e.error == "actNotFound":
            # faucet gen has not fully gone through, try again
            return None
        # some other error
        raise
