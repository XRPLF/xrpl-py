from unittest import TestCase

from xrpl.models.transactions.mptoken_authorize import MPTokenAuthorize

_ACCOUNT = "r9LqNeG6qHxjeUocjvVki2XR35weJ9mZgQ"
_TOKEN_ID = "000004C463C52827307480341125DA0577DEFC38405B0E3E"


class TestMPTokenAuthorize(TestCase):
    def test_tx_is_valid(self):
        tx = MPTokenAuthorize(
            account=_ACCOUNT,
            mptoken_issuance_id=_TOKEN_ID,
        )
        self.assertTrue(tx.is_valid())

    def test_holder(self):
        tx = MPTokenAuthorize(
            account=_ACCOUNT,
            holder="rajgkBmMxmz161r8bWYH7CQAFZP5bA9oSG",
            mptoken_issuance_id=_TOKEN_ID,
        )
        self.assertTrue(tx.is_valid())
