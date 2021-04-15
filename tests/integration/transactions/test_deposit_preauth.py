from unittest import TestCase

from tests.integration.it_utils import submit_transaction
from tests.integration.reusable_values import WALLET
from xrpl.models.exceptions import XRPLException
from xrpl.models.response import ResponseStatus
from xrpl.models.transactions import DepositPreauth

ACCOUNT = WALLET.classic_address
ADDRESS = "rEhxGqkqPPSxQ3P25J66ft5TwpzV14k2de"
FEE = "3000000"


class TestDepositPreauth(TestCase):
    def test_authorize(self):
        deposit_preauth = DepositPreauth(
            account=ACCOUNT,
            sequence=WALLET.sequence,
            authorize=ADDRESS,
        )
        response = submit_transaction(deposit_preauth, WALLET)
        self.assertEqual(response.status, ResponseStatus.SUCCESS)
        WALLET.sequence += 1

    def test_unauthorize(self):
        deposit_preauth = DepositPreauth(
            account=ACCOUNT,
            sequence=WALLET.sequence,
            unauthorize=ADDRESS,
        )
        response = submit_transaction(deposit_preauth, WALLET)
        self.assertEqual(response.status, ResponseStatus.SUCCESS)
        WALLET.sequence += 1

    def test_high_fee_unauthorized(self):
        # GIVEN a new DepositPreauth transaction
        deposit_preauth = DepositPreauth(
            account=ACCOUNT,
            sequence=WALLET.sequence,
            unauthorize=ADDRESS,
            # WITH fee higher than 2 XRP
            fee=FEE,
        )
        # We expect an XRPLException to be raised
        with self.assertRaises(XRPLException):
            # WITH the default Json RPC Client which doesn't
            # allow more than 2 XRP fee
            submit_transaction(deposit_preauth, WALLET)
