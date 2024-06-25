from unittest import TestCase

from xrpl.models.ledger_objects.fee_settings import FeeSettings
from xrpl.models.ledger_objects.ledger_object import LedgerObject


class TestFeeSettings(TestCase):
    def test_fee_settings(self):
        fee_settings_json = {
            "BaseFee": "000000000000000A",
            "Flags": 0,
            "LedgerEntryType": "FeeSettings",
            "ReferenceFeeUnits": 10,
            "ReserveBase": 20000000,
            "ReserveIncrement": 5000000,
            "index": "4BC50C9B0D8515D3EAAE1E74B29A95804346C491EE1A95BF25E4AAB854A6A651",
        }
        actual = LedgerObject.from_xrpl(fee_settings_json)
        expected = FeeSettings(
            index="4BC50C9B0D8515D3EAAE1E74B29A95804346C491EE1A95BF25E4AAB854A6A651",
            base_fee="000000000000000A",
            reference_fee_units=10,
            reserve_base=20000000,
            reserve_increment=5000000,
        )
        self.assertEqual(actual, expected)
