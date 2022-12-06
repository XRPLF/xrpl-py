from tests.integration.integration_test_case import IntegrationTestCase
from tests.integration.it_utils import test_async_and_sync
from tests.integration.reusable_values import WALLET
from xrpl.asyncio.transaction import autofill_and_sign
from xrpl.core.binarycodec import encode
from xrpl.models.amounts import IssuedCurrencyAmount
from xrpl.models.requests import SubmitOnly
from xrpl.models.transactions import OfferCreate

TX = OfferCreate(
    account=WALLET.classic_address,
    sequence=WALLET.sequence,
    last_ledger_sequence=WALLET.sequence + 10,
    taker_gets="13100000",
    taker_pays=IssuedCurrencyAmount(
        currency="USD",
        issuer=WALLET.classic_address,
        value="10",
    ),
)


class TestSubmitOnly(IntegrationTestCase):
    @test_async_and_sync(globals(), ["xrpl.transaction.autofill_and_sign"])
    async def test_basic_functionality(self, client):
        transaction = await autofill_and_sign(TX, WALLET, client)
        tx_json = transaction.to_xrpl()
        tx_blob = encode(tx_json)
        response = await client.request(
            SubmitOnly(
                tx_blob=tx_blob,
            )
        )
        self.assertTrue(response.is_successful())
