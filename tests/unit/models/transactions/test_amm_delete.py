from unittest import TestCase

from xrpl.models.currencies import XRP, IssuedCurrency
from xrpl.models.transactions import AMMDelete


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
