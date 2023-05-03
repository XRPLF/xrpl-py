from tests.integration.integration_test_case import IntegrationTestCase
from tests.integration.it_utils import (
    accept_ledger_async,
    sign_and_reliable_submission_async,
    test_async_and_sync,
)
from tests.integration.reusable_values import DESTINATION, WALLET
from xrpl.models.requests import StreamParameter, Subscribe
from xrpl.models.requests.unsubscribe import Unsubscribe
from xrpl.models.transactions.payment import Payment

_MESSAGE_LIMIT = 3


# For tests that don't rely on the testnet, we use a local rippled server
# where we can force accept ledger. This is a lot faster than waiting for
# the testnet to accept a ledger. In these, an initial message is
# always sent to the client when they subscribe, so we do not need to
# send a ledger accept call before the async for loop.
class TestSubscribe(IntegrationTestCase):
    @test_async_and_sync(globals(), websockets_only=True)
    async def test_ledger_subscription(self, client):
        await client.send(Subscribe(streams=[StreamParameter.LEDGER]))
        count = 0
        async for message in client:
            await accept_ledger_async()
            if count == 0:
                self.assertIsInstance(message["result"]["ledger_index"], int)
            else:
                self.assertIsInstance(message["ledger_index"], int)
            if count == _MESSAGE_LIMIT:
                break
            count += 1

        await client.send(Unsubscribe(streams=[StreamParameter.LEDGER]))
        async for message in client:
            self.assertEqual(message["status"], "success")
            break

    @test_async_and_sync(globals(), websockets_only=True, use_testnet=True)
    async def test_validations_subscription(self, client):
        await client.send(Subscribe(streams=[StreamParameter.VALIDATIONS]))
        count = 0
        async for message in client:
            if count != 0:
                self.assertEqual(message["type"], "validationReceived")
            if count == _MESSAGE_LIMIT:
                break
            count += 1

        await client.send(Unsubscribe(streams=[StreamParameter.VALIDATIONS]))
        async for message in client:
            if "status" in message:
                self.assertEqual(message["status"], "success")
                break

    @test_async_and_sync(globals(), websockets_only=True, use_testnet=True)
    async def test_consensus_subscription(self, client):
        await client.send(Subscribe(streams=[StreamParameter.CONSENSUS]))
        count = 0
        async for message in client:
            if count != 0:
                self.assertEqual(message["type"], "consensusPhase")
            if count == _MESSAGE_LIMIT:
                break
            count += 1

        await client.send(Unsubscribe(streams=[StreamParameter.CONSENSUS]))
        async for message in client:
            if "status" in message:
                self.assertEqual(message["status"], "success")
                break

    @test_async_and_sync(globals(), websockets_only=True)
    async def test_transactions_subscription(self, client):
        await client.send(Subscribe(streams=[StreamParameter.TRANSACTIONS]))

        payment_transaction = Payment(
            account=WALLET.classic_address,
            amount="100",
            destination=DESTINATION.classic_address,
        )

        count = 0
        async for message in client:
            # TODO: refactor so this can use the same client
            await sign_and_reliable_submission_async(
                payment_transaction,
                WALLET,
            )
            if count != 0:
                self.assertEqual(message["type"], "transaction")
            if count == _MESSAGE_LIMIT:
                break
            count += 1

        await client.send(Unsubscribe(streams=[StreamParameter.TRANSACTIONS]))
        async for message in client:
            if "result" in message:
                self.assertEqual(message["result"], {})
                break

    @test_async_and_sync(globals(), websockets_only=True)
    async def test_transactions_proposed_subscription(self, client):
        await client.send(Subscribe(streams=[StreamParameter.TRANSACTIONS_PROPOSED]))

        payment_transaction = Payment(
            account=WALLET.classic_address,
            amount="100",
            destination=DESTINATION.classic_address,
        )

        count = 0
        async for message in client:
            # TODO: refactor so this can use the same client
            await sign_and_reliable_submission_async(
                payment_transaction,
                WALLET,
            )
            if count != 0:
                self.assertEqual(message["type"], "transaction")
            if count == _MESSAGE_LIMIT:
                break
            count += 1

        await client.send(Unsubscribe(streams=[StreamParameter.TRANSACTIONS_PROPOSED]))
        async for message in client:
            if "result" in message:
                self.assertEqual(message["result"], {})
                break
