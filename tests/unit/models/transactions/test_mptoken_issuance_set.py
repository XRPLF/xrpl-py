from unittest import TestCase

from xrpl.models.exceptions import XRPLModelException
from xrpl.models.transactions import MPTokenIssuanceSet
from xrpl.models.transactions.mptoken_issuance_set import MPTokenIssuanceSetFlag

_ACCOUNT = "r9LqNeG6qHxjeUocjvVki2XR35weJ9mZgQ"
_TOKEN_ID = "000004C463C52827307480341125DA0577DEFC38405B0E3E"


class TestMPTokenIssuanceSet(TestCase):
    def test_tx_is_valid(self):
        tx = MPTokenIssuanceSet(
            account=_ACCOUNT,
            mptoken_issuance_id=_TOKEN_ID,
            flags=MPTokenIssuanceSetFlag.TF_MPT_LOCK,
        )
        self.assertTrue(tx.is_valid())

    def test_tx_with_holder(self):
        tx = MPTokenIssuanceSet(
            account=_ACCOUNT,
            mptoken_issuance_id=_TOKEN_ID,
            holder="rajgkBmMxmz161r8bWYH7CQAFZP5bA9oSG",
            flags=MPTokenIssuanceSetFlag.TF_MPT_LOCK,
        )
        self.assertTrue(tx.is_valid())

    def test_tx_without_flags(self):
        # It's fine to not specify any flag, it means only tx fee is deducted
        tx = MPTokenIssuanceSet(
            account=_ACCOUNT,
            mptoken_issuance_id=_TOKEN_ID,
            holder="rajgkBmMxmz161r8bWYH7CQAFZP5bA9oSG",
        )
        self.assertTrue(tx.is_valid())

    def test_tx_with_flag_conflict(self):
        with self.assertRaises(XRPLModelException) as error:
            MPTokenIssuanceSet(
                account=_ACCOUNT,
                mptoken_issuance_id=_TOKEN_ID,
                holder="rajgkBmMxmz161r8bWYH7CQAFZP5bA9oSG",
                flags=MPTokenIssuanceSetFlag.TF_MPT_LOCK
                | MPTokenIssuanceSetFlag.TF_MPT_UNLOCK,
            )
        self.assertEqual(
            error.exception.args[0],
            "{'flags': \"flag conflict: both TF_MPT_LOCK and TF_MPT_UNLOCK can't be set"
            '"}',
        )
