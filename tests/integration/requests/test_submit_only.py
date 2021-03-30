from unittest import TestCase

from tests.integration.it_utils import JSON_RPC_CLIENT
from tests.integration.reusable_values import FEE, WALLET
from xrpl.models.amounts import IssuedCurrencyAmount
from xrpl.models.requests import SubmitOnly
from xrpl.models.transactions import OfferCreate
from xrpl.transaction import safe_sign_transaction

TX = OfferCreate(
    account=WALLET.classic_address,
    fee=FEE,
    sequence=WALLET.next_sequence_num,
    last_ledger_sequence=WALLET.next_sequence_num + 10,
    taker_gets="13100000",
    taker_pays=IssuedCurrencyAmount(
        currency="USD",
        issuer=WALLET.classic_address,
        value="10",
    ),
)
TX_BLOB = safe_sign_transaction(TX, WALLET)


class TestSubmitOnly(TestCase):
    def test_basic_functionality(self):
        response = JSON_RPC_CLIENT.request(
            SubmitOnly(
                tx_blob=TX_BLOB,
            )
        )
        self.assertTrue(response.is_successful())
