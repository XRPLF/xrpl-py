from unittest import TestCase

from tests.integration.it_utils import JSON_RPC_CLIENT
from tests.integration.reusable_values import WALLET
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
TRANSACTION = safe_sign_and_autofill_transaction(TX, WALLET, JSON_RPC_CLIENT)
TX_JSON = transaction_json_to_binary_codec_form(TRANSACTION.to_dict())
TX_BLOB = encode(TX_JSON)


class TestSubmitOnly(TestCase):
    def test_basic_functionality(self):
        response = JSON_RPC_CLIENT.request(
            SubmitOnly(
                tx_blob=TX_BLOB,
            )
        )
        self.assertTrue(response.is_successful())
