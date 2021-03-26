from unittest import TestCase

from tests.integration.it_utils import JSON_RPC_CLIENT
from tests.integration.reusable_values import WALLET
from xrpl.models.currencies import XRP, IssuedCurrency
from xrpl.models.requests import BookOffers


class TestTx(TestCase):
    def test_basic_functionality(self):
        response = JSON_RPC_CLIENT.request(
            BookOffers(
                taker=WALLET.classic_address,
                taker_gets=XRP(),
                taker_pays=IssuedCurrency(
                    currency="USD",
                    issuer="rvYAfWj5gh67oV6fW32ZzP3Aw4Eubs59B",
                ),
                ledger_index="validated",
            ),
        )
        print(response)
        self.assertTrue(response.is_successful())
