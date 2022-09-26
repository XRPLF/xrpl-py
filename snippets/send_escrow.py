"""A snippet that walks us through creating and finishing escrows."""
from datetime import datetime

from xrpl.account import get_balance
from xrpl.clients import JsonRpcClient
from xrpl.models.requests import AccountObjects
from xrpl.models.transactions import EscrowCreate, EscrowFinish
from xrpl.transaction import (
    safe_sign_and_autofill_transaction,
    send_reliable_submission,
)
from xrpl.utils import datetime_to_ripple_time
from xrpl.wallet import generate_faucet_wallet


def send_escrow(client: JsonRpcClient) -> None:
    """
    Sync snippet that walks us through creating and finishing escrows.

    Args:
        client: The network client to use to send the request.
    """
    # creating wallets as prerequisite
    wallet1 = generate_faucet_wallet(client, debug=True)
    wallet2 = generate_faucet_wallet(client, debug=True)

    print("Balances of wallets before Escrow tx was created:")
    print(get_balance(wallet1.classic_address, client))
    print(get_balance(wallet2.classic_address, client))

    finish_after = datetime_to_ripple_time(datetime.now()) + 2

    create_tx = EscrowCreate(
        account=wallet1.classic_address,
        destination=wallet2.classic_address,
        amount="1000000",
        finish_after=finish_after,
    )

    signed_create_tx = safe_sign_and_autofill_transaction(create_tx, wallet1, client)
    create_escrow_response = send_reliable_submission(signed_create_tx, client)

    print(create_escrow_response)

    # check that the object was actually created
    account_objects_request = AccountObjects(account=wallet1.classic_address)
    account_objects = (client.request(account_objects_request)).result[
        "account_objects"
    ]

    print("Escrow object exists in wallet1's account")
    print(account_objects)

    finish_tx = EscrowFinish(
        account=wallet1.classic_address,
        owner=wallet1.classic_address,
        offer_sequence=create_escrow_response.result["Sequence"],
    )

    signed_finish_tx = safe_sign_and_autofill_transaction(finish_tx, wallet1, client)
    send_reliable_submission(signed_finish_tx, client)

    print("Balances of wallets after Escrow was sent")
    print(get_balance(wallet1.classic_address, client))
    print(get_balance(wallet2.classic_address, client))


# uncomment the lines below to run the snippet
# client = JsonRpcClient("https://s.altnet.rippletest.net:51234/")
# send_escrow(client)
