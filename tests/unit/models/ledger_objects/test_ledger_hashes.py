from unittest import TestCase

from xrpl.models.ledger_objects.ledger_hashes import LedgerHashes
from xrpl.models.ledger_objects.ledger_object import LedgerObject


class TestLedgerHashes(TestCase):
    def test_ledger_hashes(self):
        ledger_hashes_json = {
            "LedgerEntryType": "LedgerHashes",
            "Flags": 0,
            "FirstLedgerSequence": 2,
            "LastLedgerSequence": 33872029,
            "Hashes": [
                "D638208ADBD04CBB10DE7B645D3AB4BA31489379411A3A347151702B6401AA78",
                "254D690864E418DDD9BCAC93F41B1F53B1AE693FC5FE667CE40205C322D1BE3B",
                "A2B31D28905E2DEF926362822BC412B12ABF6942B73B72A32D46ED2ABB7ACCFA",
                "AB4014846DF818A4B43D6B1686D0DE0644FE711577C5AB6F0B2A21CCEE280140",
                "3383784E82A8BA45F4DD5EF4EE90A1B2D3B4571317DBAC37B859836ADDE644C1",
            ],
            "index": "B4979A36CDC7F3D3D5C31A4EAE2AC7D7209DDA877588B9AFC66799692AB0D66B",
        }
        actual = LedgerObject.from_xrpl(ledger_hashes_json)
        expected = LedgerHashes(
            index="B4979A36CDC7F3D3D5C31A4EAE2AC7D7209DDA877588B9AFC66799692AB0D66B",
            first_ledger_sequence=2,
            last_ledger_sequence=33872029,
            hashes=[
                "D638208ADBD04CBB10DE7B645D3AB4BA31489379411A3A347151702B6401AA78",
                "254D690864E418DDD9BCAC93F41B1F53B1AE693FC5FE667CE40205C322D1BE3B",
                "A2B31D28905E2DEF926362822BC412B12ABF6942B73B72A32D46ED2ABB7ACCFA",
                "AB4014846DF818A4B43D6B1686D0DE0644FE711577C5AB6F0B2A21CCEE280140",
                "3383784E82A8BA45F4DD5EF4EE90A1B2D3B4571317DBAC37B859836ADDE644C1",
            ],
        )
        self.assertEqual(actual, expected)