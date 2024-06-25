from unittest import TestCase

from xrpl.models.ledger_objects.ledger_object import LedgerObject
from xrpl.models.ledger_objects.negative_unl import DisabledValidator, NegativeUNL


class TestNegativeUNL(TestCase):
    def test_negative_unl(self):
        negative_unl_json = {
            "DisabledValidators": [
                {
                    "DisabledValidator": {
                        "FirstLedgerSequence": 1609728,
                        "PublicKey": "ED6629D456285AE3613B285F65BBFF168D695BA"
                        "3921F309949AFCD2CA7AFEC16FE",
                    }
                }
            ],
            "Flags": 0,
            "LedgerEntryType": "NegativeUNL",
            "index": "2E8A59AA9D3B5B186B0B9E0F62E6C02587CA74A4D778938E957B6357D364B244",
        }
        actual = LedgerObject.from_xrpl(negative_unl_json)
        expected = NegativeUNL(
            index="2E8A59AA9D3B5B186B0B9E0F62E6C02587CA74A4D778938E957B6357D364B244",
            disabled_validators=[
                DisabledValidator(
                    first_ledger_sequence=1609728,
                    public_key="ED6629D456285AE3613B285F65BBFF168D695BA"
                    "3921F309949AFCD2CA7AFEC16FE",
                )
            ],
        )
        self.assertEqual(actual, expected)
