from tests.integration.integration_test_case import IntegrationTestCase
from tests.integration.it_utils import (
    fund_wallet_async,
    sign_and_reliable_submission_async,
    test_async_and_sync,
)
from tests.integration.reusable_values import DESTINATION, WALLET
from xrpl.asyncio.transaction import autofill
from xrpl.models import Batch, BatchFlag, Payment, TicketCreate
from xrpl.models.requests.account_objects import AccountObjects, AccountObjectType
from xrpl.models.response import ResponseStatus
from xrpl.transaction.batch_signers import (
    combine_batch_signers,
    sign_multiaccount_batch,
)
from xrpl.wallet import Wallet


class TestBatch(IntegrationTestCase):
    @test_async_and_sync(globals())
    async def test_all_or_nothing(self, client):
        payment = Payment(
            account=WALLET.address,
            amount="1",
            destination=DESTINATION.address,
        )
        batch = Batch(
            account=WALLET.address,
            flags=BatchFlag.TF_ALL_OR_NOTHING,
            raw_transactions=[payment, payment],
        )
        response = await sign_and_reliable_submission_async(batch, WALLET, client)
        self.assertEqual(response.status, ResponseStatus.SUCCESS)
        self.assertEqual(response.result["engine_result"], "tesSUCCESS")

    @test_async_and_sync(globals())
    async def test_independent(self, client):
        payment = Payment(
            account=WALLET.address,
            amount="1",
            destination=DESTINATION.address,
        )
        batch = Batch(
            account=WALLET.address,
            flags=BatchFlag.TF_INDEPENDENT,
            raw_transactions=[payment, payment],
        )
        response = await sign_and_reliable_submission_async(batch, WALLET, client)
        self.assertEqual(response.status, ResponseStatus.SUCCESS)
        self.assertEqual(response.result["engine_result"], "tesSUCCESS")

    @test_async_and_sync(globals(), ["xrpl.transaction.autofill"])
    async def test_multi_account_single_sign(self, client):
        payment = Payment(
            account=WALLET.address,
            amount="1",
            destination=DESTINATION.address,
        )
        payment2 = Payment(
            account=DESTINATION.address,
            amount="1",
            destination=WALLET.address,
        )
        batch = Batch(
            account=WALLET.address,
            flags=BatchFlag.TF_ALL_OR_NOTHING,
            raw_transactions=[payment, payment2],
        )
        autofilled = await autofill(batch, client, 1)
        signed = sign_multiaccount_batch(DESTINATION, autofilled)
        response = await sign_and_reliable_submission_async(signed, WALLET, client)
        self.assertEqual(response.status, ResponseStatus.SUCCESS)
        self.assertEqual(response.result["engine_result"], "tesSUCCESS")

    @test_async_and_sync(globals(), ["xrpl.transaction.autofill"])
    async def test_combine_batch_signers(self, client):
        signer = Wallet.create()
        await fund_wallet_async(signer)
        batch = Batch(
            account=WALLET.address,
            flags=BatchFlag.TF_ALL_OR_NOTHING,
            raw_transactions=[
                Payment(
                    account=WALLET.address,
                    amount="1",
                    destination=DESTINATION.address,
                ),
                Payment(
                    account=DESTINATION.address,
                    amount="1",
                    destination=WALLET.address,
                ),
                Payment(
                    account=signer.address,
                    amount="1",
                    destination=WALLET.address,
                ),
            ],
        )
        autofilled = await autofill(batch, client, 2)
        signed_dest = sign_multiaccount_batch(DESTINATION, autofilled)
        signed_signer = sign_multiaccount_batch(signer, autofilled)
        combined = Batch.from_blob(combine_batch_signers([signed_dest, signed_signer]))
        response = await sign_and_reliable_submission_async(combined, WALLET, client)
        self.assertEqual(response.status, ResponseStatus.SUCCESS)
        self.assertEqual(response.result["engine_result"], "tesSUCCESS")

    @test_async_and_sync(globals(), ["xrpl.transaction.autofill"])
    async def test_ticket_sequence(self, client):
        # The V1_1 signing payload binds the outer sequence value, which is the
        # TicketSequence when a ticket is used. This exercises that path.
        await sign_and_reliable_submission_async(
            TicketCreate(account=WALLET.address, ticket_count=1), WALLET, client
        )
        ticket_objects = await client.request(
            AccountObjects(account=WALLET.address, type=AccountObjectType.TICKET)
        )
        ticket_sequence = max(
            obj["TicketSequence"] for obj in ticket_objects.result["account_objects"]
        )

        batch = Batch(
            account=WALLET.address,
            flags=BatchFlag.TF_ALL_OR_NOTHING,
            sequence=0,
            ticket_sequence=ticket_sequence,
            raw_transactions=[
                Payment(
                    account=WALLET.address,
                    amount="1",
                    destination=DESTINATION.address,
                ),
                Payment(
                    account=DESTINATION.address,
                    amount="1",
                    destination=WALLET.address,
                ),
            ],
        )
        autofilled = await autofill(batch, client, 1)
        signed = sign_multiaccount_batch(DESTINATION, autofilled)
        response = await sign_and_reliable_submission_async(signed, WALLET, client)
        self.assertEqual(response.status, ResponseStatus.SUCCESS)
        self.assertEqual(response.result["engine_result"], "tesSUCCESS")
