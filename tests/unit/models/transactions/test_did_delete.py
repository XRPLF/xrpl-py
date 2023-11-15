from unittest import TestCase

from xrpl.models.transactions import DIDDelete

_ACCOUNT = "r9LqNeG6qHxjeUocjvVki2XR35weJ9mZgQ"


class TestDIDDelete(TestCase):
    def test_valid(self):
        tx = DIDDelete(
            account=_ACCOUNT,
        )
        self.assertTrue(tx.is_valid())
