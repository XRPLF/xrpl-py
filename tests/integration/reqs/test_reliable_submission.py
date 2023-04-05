from tests.integration.integration_test_case import IntegrationTestCase
from tests.integration.it_utils import test_async_and_sync
from tests.integration.reusable_values import WALLET
from xrpl.asyncio.transaction import autofill_and_sign
from xrpl.asyncio.transaction.reliable_submission import XRPLReliableSubmissionException
from xrpl.models.amounts import IssuedCurrencyAmount
from xrpl.models.requests.generic_request import GenericRequest
from xrpl.models.transactions import OfferCreate
from xrpl.transaction.reliable_submission import send_reliable_submission

sequence_buffer = 2

TX = OfferCreate(
    account=WALLET.classic_address,
    sequence=WALLET.sequence,
    last_ledger_sequence=WALLET.sequence + sequence_buffer,
    taker_gets="13100000",
    taker_pays=IssuedCurrencyAmount(
        currency="USD",
        issuer=WALLET.classic_address,
        value="10",
    ),
)


class TestSubmitOnly(IntegrationTestCase):
    @test_async_and_sync(globals(), ["xrpl.transaction.autofill_and_sign", 
                                     "xrpl.transaction.reliable_submission"])
    async def succeeds_with_basic_transaction(self, client):
        transaction = await autofill_and_sign(TX, WALLET, client)
        for _ in range(sequence_buffer + 1):
            client.request(GenericRequest(method="ledger_accept"))

        tx_json = transaction.to_xrpl()
        response = await send_reliable_submission(tx_json, client)
        self.assertEqual(response.result["engine_result"], "tesSUCCESS")

    @test_async_and_sync(globals(), ["xrpl.transaction.autofill_and_sign", 
                                     "xrpl.transaction.reliable_submission"])
    async def fails_after_ledger_sequence_past(self, client):
        transaction = await autofill_and_sign(TX, WALLET, client)
        for _ in range(sequence_buffer + 1):
            client.request(GenericRequest(method="ledger_accept"))

        tx_json = transaction.to_xrpl()
        with self.assertRaises(XRPLReliableSubmissionException):
            await send_reliable_submission(tx_json, client)
