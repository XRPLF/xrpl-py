from unittest import TestCase

from tests.integration.it_utils import (
    JSON_RPC_CLIENT_WITH_CUSTOM_PARAMETERS,
    submit_transaction,
)
from tests.integration.reusable_values import PAYMENT_CHANNEL, WALLET
from xrpl.models.exceptions import XRPLException
from xrpl.models.transactions import PaymentChannelFund

FEE = "3000000"


class TestPaymentChannelFund(TestCase):
    def test_basic_functionality(self):
        response = submit_transaction(
            PaymentChannelFund(
                account=WALLET.classic_address,
                sequence=WALLET.sequence,
                channel=PAYMENT_CHANNEL.result["hash"],
                amount="1",
            ),
            WALLET,
        )
        self.assertTrue(response.is_successful())

    def test_high_fee_unauthorized(self):
        # We expect an XRPLException to be raised
        with self.assertRaises(XRPLException):
            submit_transaction(
                # GIVEN a new PaymentChannelFund transaction
                PaymentChannelFund(
                    account=WALLET.classic_address,
                    sequence=WALLET.sequence,
                    channel=PAYMENT_CHANNEL.result["hash"],
                    amount="1",
                    # WITH the fee higher than 2 XRP
                    fee=FEE,
                ),
                WALLET,
                # WITH the default Json RPC Client which doesn't
                # allow more than 2 XRP fee
            )

    def test_high_fee_authorized(self):
        # GIVEN a new PaymentChannelFund transaction
        response = submit_transaction(
            # GIVEN a new PaymentChannelFund transaction
            PaymentChannelFund(
                account=WALLET.classic_address,
                sequence=WALLET.sequence,
                channel=PAYMENT_CHANNEL.result["hash"],
                amount="1",
                # WITH the fee higher than 2 XRP
                fee=FEE,
            ),
            WALLET,
            # WITH the Json RPC Client allowing more than 2 XRP
            JSON_RPC_CLIENT_WITH_CUSTOM_PARAMETERS,
        )

        self.assertTrue(response.is_successful())
        WALLET.sequence += 1
