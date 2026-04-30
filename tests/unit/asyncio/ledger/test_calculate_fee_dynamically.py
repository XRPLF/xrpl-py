from unittest import TestCase

from xrpl.asyncio.ledger.main import calculate_fee_dynamically


class TestCalculateFeeDynamically(TestCase):
    def test_queue_empty(self):
        actual = {
            "current_ledger_size": "46",
            "current_queue_size": "0",
            "drops": {
                "base_fee": "10",
                "median_fee": "5000",
                "minimum_fee": "10",
                "open_ledger_fee": "10",
            },
            "expected_ledger_size": "176",
            "ledger_current_index": 70813866,
            "levels": {
                "median_level": "128000",
                "minimum_level": "256",
                "open_ledger_level": "256",
                "reference_level": "256",
            },
            "max_queue_size": "3520",
        }
        expected = "15"
        self.assertEqual(calculate_fee_dynamically(fee_data_set=actual), expected)

    def test_queue_partially_filled(self):
        actual = {
            "current_ledger_size": "46",
            "current_queue_size": "1760",
            "drops": {
                "base_fee": "10",
                "median_fee": "5000",
                "minimum_fee": "10",
                "open_ledger_fee": "10",
            },
            "expected_ledger_size": "176",
            "ledger_current_index": 70813866,
            "levels": {
                "median_level": "128000",
                "minimum_level": "256",
                "open_ledger_level": "256",
                "reference_level": "256",
            },
            "max_queue_size": "3520",
        }
        expected = "225"
        self.assertEqual(calculate_fee_dynamically(fee_data_set=actual), expected)

    def test_queue_full(self):
        actual = {
            "current_ledger_size": "46",
            "current_queue_size": "3520",
            "drops": {
                "base_fee": "10",
                "median_fee": "5000",
                "minimum_fee": "10",
                "open_ledger_fee": "10",
            },
            "expected_ledger_size": "176",
            "ledger_current_index": 70813866,
            "levels": {
                "median_level": "128000",
                "minimum_level": "256",
                "open_ledger_level": "256",
                "reference_level": "256",
            },
            "max_queue_size": "3520",
        }
        expected = "5500"
        self.assertEqual(calculate_fee_dynamically(fee_data_set=actual), expected)
