"""A snippet that walks us through using a partial payment."""
from xrpl.asyncio.clients import AsyncWebsocketClient
from xrpl.asyncio.transaction import (
    safe_sign_and_autofill_transaction,
    send_reliable_submission,
)
from xrpl.asyncio.wallet import generate_faucet_wallet
from xrpl.models.amounts import IssuedCurrencyAmount
from xrpl.models.requests import AccountLines
from xrpl.models.transactions import Payment, PaymentFlag, TrustSet


async def async_partial_payment() -> None:
    """
    Async snippet that walks us through using a partial payment.

    Args:
        client: The async network client to use to send the request.
    """
    async with AsyncWebsocketClient("wss://s.altnet.rippletest.net:51233") as client:
        await client.open()

        # creating wallets as prerequisite
        wallet1 = await generate_faucet_wallet(client, debug=True)
        wallet2 = await generate_faucet_wallet(client, debug=True)

        # create a trustline to issue an IOU `FOO` and set limit on it
        trust_set_tx = TrustSet(
            account=wallet2.classic_address,
            limit_amount=IssuedCurrencyAmount(
                currency="FOO",
                value="10000000000",
                issuer=wallet1.classic_address,
            ),
        )

        signed_trust_set_tx = await safe_sign_and_autofill_transaction(
            trust_set_tx, wallet2, client
        )
        await send_reliable_submission(signed_trust_set_tx, client)

        print("Balances after trustline is claimed:")
        print(
            (await client.request(AccountLines(account=wallet1.classic_address))).result[
                "lines"
            ]
        )
        print(
            (await client.request(AccountLines(account=wallet2.classic_address))).result[
                "lines"
            ]
        )

        # initially, the issuer(wallet1) sends an amount to the other account(wallet2)
        issue_quantity = "3840"
        payment_tx = Payment(
            account=wallet1.classic_address,
            amount=IssuedCurrencyAmount(
                currency="FOO",
                value=issue_quantity,
                issuer=wallet1.classic_address,
            ),
            destination=wallet2.classic_address,
        )

        # submit payment
        signed_payment_tx = await safe_sign_and_autofill_transaction(
            payment_tx, wallet1, client
        )
        payment_response = await send_reliable_submission(signed_payment_tx, client)
        print(payment_response)

        print("Balances after wallet1 sends 3840 FOO to wallet2:")
        print(
            (await client.request(AccountLines(account=wallet1.classic_address))).result[
                "lines"
            ]
        )
        print(
            (await client.request(AccountLines(account=wallet2.classic_address))).result[
                "lines"
            ]
        )

        # Send money less than the amount specified on 2 conditions:
        # 1. Sender has less money than the aamount specified in the payment Tx.
        # 2. Sender has the tfPartialPayment flag activated.

        # Other ways to specify flags are by using Hex code and decimal code.
        # eg. For partial payment(tfPartialPayment)
        # decimal ->131072, hex -> 0x00020000
        partial_payment_tx = Payment(
            account=wallet2.classic_address,
            amount=IssuedCurrencyAmount(
                currency="FOO",
                value="4000",
                issuer=wallet1.classic_address,
            ),
            destination=wallet1.classic_address,
            flags=[PaymentFlag.TF_PARTIAL_PAYMENT],
            send_max=IssuedCurrencyAmount(
                currency="FOO",
                value="1000000",
                issuer=wallet1.classic_address,
            ),
        )

        # submit payment
        signed_partial_payment_tx = await safe_sign_and_autofill_transaction(
            partial_payment_tx, wallet2, client
        )
        partial_payment_response = await send_reliable_submission(
            signed_partial_payment_tx, client
        )
        print(partial_payment_response)

        print("Balances after Partial Payment, when wallet2 tried to send 4000 FOOs")
        print(
            (await client.request(AccountLines(account=wallet1.classic_address))).result[
                "lines"
            ]
        )
        print(
            (await client.request(AccountLines(account=wallet2.classic_address))).result[
                "lines"
            ]
        )

        await client.close()


# uncomment the lines below to run the snippet
# import asyncio
# asyncio.run(async_partial_payment())
