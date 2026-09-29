from unittest import TestCase

from xrpl.core.binarycodec import decode
from xrpl.models.currencies import XRP, IssuedCurrency, MPTCurrency
from xrpl.models.transactions import AMMDelete

_MPT_ID = "00000003430427B80BD2D09D36B70B969E12801065F22308"
_MPT_ID2 = "00000004430427B80BD2D09D36B70B969E12801065F22308"


class TestAMMDeposit(TestCase):
    def test_tx_valid(self):
        tx = AMMDelete(
            account="r9LqNeG6qHxjeUocjvVki2XR35weJ9mZgQ",
            sequence=1337,
            asset=XRP(),
            asset2=IssuedCurrency(
                currency="ETH", issuer="rpGtkFRXhgVaBzC5XCR7gyE2AZN5SN3SEW"
            ),
        )
        self.assertTrue(tx.is_valid())

    def test_tx_valid_with_mpt(self):
        tx = AMMDelete(
            account="r9LqNeG6qHxjeUocjvVki2XR35weJ9mZgQ",
            asset=MPTCurrency(mpt_issuance_id=_MPT_ID),
            asset2=MPTCurrency(mpt_issuance_id=_MPT_ID2),
        )
        self.assertTrue(tx.is_valid())
        self.assertEqual(decode(tx.blob()), tx.to_xrpl())
