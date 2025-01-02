from unittest import TestCase

from xrpl.models.transactions.mptoken_issuance_destroy import MPTokenIssuanceDestroy

_ACCOUNT = "r9LqNeG6qHxjeUocjvVki2XR35weJ9mZgQ"
_TOKEN_ID = "000004C463C52827307480341125DA0577DEFC38405B0E3E"


class TestMPTokenIssuanceDestroy(TestCase):
    def test_tx_is_valid(self):
        tx = MPTokenIssuanceDestroy(
            account=_ACCOUNT,
            mptoken_issuance_id=_TOKEN_ID,
        )
        self.assertTrue(tx.is_valid())
