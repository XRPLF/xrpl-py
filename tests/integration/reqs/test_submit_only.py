from tests.integration.integration_test_case import IntegrationTestCase
from tests.integration.it_utils import JSON_RPC_CLIENT, test_async_and_sync
from tests.integration.reusable_values import WALLET
from xrpl.account import get_next_valid_seq_number
from xrpl.asyncio.transaction import (
    safe_sign_and_autofill_transaction as safe_sign_and_autofill_transaction_async,
)
from xrpl.core.binarycodec import encode
from xrpl.models.amounts import IssuedCurrencyAmount
from xrpl.models.requests import SubmitOnly
from xrpl.models.transactions import OfferCreate

SEQ = get_next_valid_seq_number(WALLET.classic_address, JSON_RPC_CLIENT)

TX = OfferCreate(
    account=WALLET.classic_address,
    sequence=SEQ,
    last_ledger_sequence=SEQ + 10,
    taker_gets="13100000",
    taker_pays=IssuedCurrencyAmount(
        currency="USD",
        issuer=WALLET.classic_address,
        value="10",
    ),
)


class TestSubmitOnly(IntegrationTestCase):
    @test_async_and_sync(globals())
    async def test_basic_functionality(self, client):
        transaction = await safe_sign_and_autofill_transaction_async(TX, WALLET, client)
        tx_json = transaction.to_xrpl()
        tx_blob = encode(tx_json)
        response = await client.request(
            SubmitOnly(
                tx_blob=tx_blob,
            )
        )
        self.assertTrue(response.is_successful())
