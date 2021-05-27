try:
    from unittest import IsolatedAsyncioTestCase
except ImportError:
    from aiounittest import AsyncTestCase as IsolatedAsyncioTestCase

from tests.integration.it_utils import ASYNC_JSON_RPC_CLIENT, JSON_RPC_CLIENT
from tests.integration.reusable_values import WALLET
from xrpl.asyncio.transaction import (
    safe_sign_and_autofill_transaction as safe_sign_and_autofill_transaction_async,
)
from xrpl.asyncio.transaction import (
    transaction_json_to_binary_codec_form as transaction_to_binary_async,
)
from xrpl.core.binarycodec import encode
from xrpl.models.amounts import IssuedCurrencyAmount
from xrpl.models.requests import SubmitOnly
from xrpl.models.transactions import OfferCreate
from xrpl.transaction import (
    safe_sign_and_autofill_transaction,
    transaction_json_to_binary_codec_form,
)

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
    def test_basic_functionality_sync(self):
        transaction = safe_sign_and_autofill_transaction(TX, WALLET, JSON_RPC_CLIENT)
        tx_json = transaction_json_to_binary_codec_form(transaction.to_dict())
        tx_blob = encode(tx_json)
        response = JSON_RPC_CLIENT.request(
            SubmitOnly(
                tx_blob=tx_blob,
            )
        )
        self.assertTrue(response.is_successful())

    async def test_basic_functionality_async(self):
        transaction = await safe_sign_and_autofill_transaction_async(
            TX, WALLET, ASYNC_JSON_RPC_CLIENT
        )
        tx_json = transaction_to_binary_async(transaction.to_dict())
        tx_blob = encode(tx_json)
        response = await ASYNC_JSON_RPC_CLIENT.request(
            SubmitOnly(
                tx_blob=tx_blob,
            )
        )
        self.assertTrue(response.is_successful())
