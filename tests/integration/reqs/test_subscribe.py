from asyncio import sleep

from tests.integration.integration_test_case import IntegrationTestCase
from tests.integration.it_utils import test_async_and_sync
from xrpl.models.requests import StreamParameter, Subscribe
from xrpl.models.requests.unsubscribe import Unsubscribe

_MESSAGE_LIMIT = 3


class TestSubscribe(IntegrationTestCase):
    @test_async_and_sync(globals(), websockets_only=True)
    async def test_ledger_subscription(self, client):
        await client.send(Subscribe(streams=[StreamParameter.LEDGER]))
        count = 0
        async for message in client:
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

    @test_async_and_sync(globals(), websockets_only=True)
    async def test_callback(self, client):
        streams = []

        def callback(stream) -> None:
            self.assertIsInstance(stream["ledger_index"], int)
            streams.append(stream)

        client.on("ledgerClosed", callback)
        await client.send(Subscribe(streams=[StreamParameter.LEDGER]))

        while len(streams) < 1:
            await sleep(1)

        await client.send(Unsubscribe(streams=[StreamParameter.LEDGER]))

    @test_async_and_sync(globals(), websockets_only=True)
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

    @test_async_and_sync(globals(), websockets_only=True)
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
        count = 0
        async for message in client:
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
        count = 0
        async for message in client:
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
