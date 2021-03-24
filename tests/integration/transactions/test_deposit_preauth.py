from unittest import TestCase

from tests.integration.it_utils import submit_transaction
from tests.integration.reusable_values import WALLET
from xrpl.models.response import ResponseStatus
from xrpl.models.transactions import DepositPreauth

ACCOUNT = WALLET.classic_address
ADDRESS = "rEhxGqkqPPSxQ3P25J66ft5TwpzV14k2de"


class TestDepositPreauth(TestCase):
    def test_authorize(self):
        deposit_preauth = DepositPreauth(
            account=ACCOUNT,
            sequence=WALLET.next_sequence_num,
            authorize=ADDRESS,
        )
        response = submit_transaction(deposit_preauth, WALLET)
        self.assertEqual(response.status, ResponseStatus.SUCCESS)
        WALLET.next_sequence_num += 1

    def test_unauthorize(self):
        deposit_preauth = DepositPreauth(
            account=ACCOUNT,
            sequence=WALLET.next_sequence_num,
            unauthorize=ADDRESS,
        )
        response = submit_transaction(deposit_preauth, WALLET)
        self.assertEqual(response.status, ResponseStatus.SUCCESS)
        WALLET.next_sequence_num += 1
