from unittest import TestCase

from tests.integration.reusable_values import OFFER


class TestOfferCreate(TestCase):
    def test_all_fields(self):
        # we already create this elsewhere
        self.assertTrue(OFFER.is_successful())
