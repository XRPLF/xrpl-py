from unittest import TestCase

from tests.integration.reusable_values import PAYMENT_CHANNEL


class TestPaymentChannelCreate(TestCase):
    def test_basic_functionality(self):
        # we're already requiring this elsewhere
        self.assertTrue(PAYMENT_CHANNEL.is_successful())
