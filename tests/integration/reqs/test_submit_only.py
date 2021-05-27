try:
    from unittest import IsolatedAsyncioTestCase
except ImportError:
    from aiounittest import AsyncTestCase as IsolatedAsyncioTestCase

from tests.integration.it_utils import test_async_and_sync
from tests.integration.reusable_values import WALLET
from xrpl.asyncio.transaction import (
    safe_sign_and_autofill_transaction as safe_sign_and_autofill_transaction_async,
)
from xrpl.core.binarycodec import encode
from xrpl.models.amounts import IssuedCurrencyAmount
from xrpl.models.requests import SubmitOnly
from xrpl.models.transactions import OfferCreate
from xrpl.transaction import transaction_json_to_binary_codec_form

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


class TestSubmitOnly(IsolatedAsyncioTestCase):
    @test_async_and_sync(globals())
    async def test_basic_functionality(self, client):
        transaction = await safe_sign_and_autofill_transaction_async(TX, WALLET, client)
        tx_json = transaction_json_to_binary_codec_form(transaction.to_dict())
        tx_blob = encode(tx_json)
        response = await client.request(
            SubmitOnly(
                tx_blob=tx_blob,
            )
        )
        self.assertTrue(response.is_successful())
