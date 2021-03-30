from unittest import TestCase

from tests.integration.it_utils import submit_transaction
from tests.integration.reusable_values import WALLET
from xrpl.models.transactions import SetRegularKey
from xrpl.wallet import Wallet


class TestSetRegularKey(TestCase):
    def test_all_fields(self):
        regular_key = Wallet.create().classic_address
        response = submit_transaction(
            SetRegularKey(
                account=WALLET.classic_address,
                sequence=WALLET.sequence,
                regular_key=regular_key,
            ),
            WALLET,
        )
        self.assertTrue(response.is_successful())
        WALLET.sequence += 1
