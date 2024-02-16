from unittest import TestCase

from xrpl.models.amounts.issued_currency_amount import IssuedCurrencyAmount
from xrpl.models.ledger_objects.ledger_object import LedgerObject
from xrpl.models.ledger_objects.ripple_state import RippleState


class TestRippleState(TestCase):
    def test_ripple_state(self):
        ripple_state_json = {
            "Balance": {
                "currency": "USD",
                "issuer": "rrrrrrrrrrrrrrrrrrrrBZbvji",
                "value": "-10",
            },
            "Flags": 393216,
            "HighLimit": {
                "currency": "USD",
                "issuer": "rf1BiGeXwwQoi8Z2ueFYTEXSwuJYfV2Jpn",
                "value": "110",
            },
            "HighNode": "0000000000000000",
            "LedgerEntryType": "RippleState",
            "LowLimit": {
                "currency": "USD",
                "issuer": "rsA2LpzuawewSBQXkiju3YQTMzW13pAAdW",
                "value": "0",
            },
            "LowNode": "0000000000000000",
            "PreviousTxnID": "E3FE6EA3D48F0C2B639448020EA4F03D"
            "4F4F8FFDB243A852A0F59177921B4879",
            "PreviousTxnLgrSeq": 14090896,
            "index": "9CA88CDEDFF9252B3DE183CE35B038F57282BC9503CDFA1923EF9A95DF0D6F7B",
        }
        actual = LedgerObject.from_xrpl(ripple_state_json)
        expected = RippleState(
            index="9CA88CDEDFF9252B3DE183CE35B038F57282BC9503CDFA1923EF9A95DF0D6F7B",
            balance=IssuedCurrencyAmount(
                currency="USD", issuer="rrrrrrrrrrrrrrrrrrrrBZbvji", value="-10"
            ),
            flags=393216,
            low_limit=IssuedCurrencyAmount(
                currency="USD", issuer="rsA2LpzuawewSBQXkiju3YQTMzW13pAAdW", value="0"
            ),
            high_limit=IssuedCurrencyAmount(
                currency="USD", issuer="rf1BiGeXwwQoi8Z2ueFYTEXSwuJYfV2Jpn", value="110"
            ),
            previous_txn_id="E3FE6EA3D48F0C2B639448020EA4F03D4F4"
            "F8FFDB243A852A0F59177921B4879",
            previous_txn_lgr_seq=14090896,
            high_node="0000000000000000",
            low_node="0000000000000000",
        )
        self.assertEqual(actual, expected)
