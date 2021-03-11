from unittest import TestCase

from xrpl.models.exceptions import XRPLModelException
from xrpl.models.transactions import SignerListSet
from xrpl.models.transactions.signer_list_set import SignerEntry

_ACCOUNT = "r9LqNeG6qHxjeUocjvVki2XR35weJ9mZgQ"
_FEE = "0.00001"
_SEQUENCE = 19048

_SIGNER_ENTRIES_VALID = [
    SignerEntry(
        account="rsA2LpzuawewSBQXkiju3YQTMzW13pAAdW",
        signer_weight=2,
    ),
    SignerEntry(
        account="rUpy3eEg8rqjqfUoLeBnZkscbKbFsKXC3v",
        signer_weight=1,
    ),
    SignerEntry(
        account="raKEEVSGnKSD9Zyvxu4z6Pqpm4ABH8FS6n",
        signer_weight=1,
    ),
]


class TestSignerListSet(TestCase):
    def test_invalid_delete_has_signer_entries(self):
        with self.assertRaises(XRPLModelException):
            SignerListSet(
                account=_ACCOUNT,
                fee=_FEE,
                sequence=_SEQUENCE,
                signer_quorum=0,
                signer_entries=_SIGNER_ENTRIES_VALID,
            )

    def test_invalid_delete_nonzero_signer_quorum(self):
        with self.assertRaises(XRPLModelException):
            SignerListSet(
                account=_ACCOUNT,
                fee=_FEE,
                sequence=_SEQUENCE,
                signer_quorum=5,
            )

    def test_invalid_signer_quorum_negative(self):
        signer_quorum = -7
        with self.assertRaises(XRPLModelException):
            SignerListSet(
                account=_ACCOUNT,
                fee=_FEE,
                sequence=_SEQUENCE,
                signer_quorum=signer_quorum,
                signer_entries=_SIGNER_ENTRIES_VALID,
            )

    def test_invalid_signer_entries_empty(self):
        with self.assertRaises(XRPLModelException):
            SignerListSet(
                account=_ACCOUNT,
                fee=_FEE,
                sequence=_SEQUENCE,
                signer_quorum=1,
                signer_entries=[],
            )

    def test_invalid_signer_entries_too_big(self):
        signer_entries = [
            SignerEntry(
                account="rsA2LpzuawewSBQXkiju3YQTMzW13pAAdW",
                signer_weight=2,
            ),
            SignerEntry(
                account="rUpy3eEg8rqjqfUoLeBnZkscbKbFsKXC3v",
                signer_weight=1,
            ),
            SignerEntry(
                account="raKEEVSGnKSD9Zyvxu4z6Pqpm4ABH8FS6n",
                signer_weight=1,
            ),
            SignerEntry(
                account="ra5nK24KXen9AHvsdFTKHSANinZseWnPcX",
                signer_weight=1,
            ),
            SignerEntry(
                account="rWYkbWkCeg8dP6rXALnjgZSjjLyih5NXm",
                signer_weight=1,
            ),
            SignerEntry(
                account="rPT1Sjq2YGrBMTttX4GZHjKu9dyfzbpAYe",
                signer_weight=1,
            ),
            SignerEntry(
                account="rsUiUMpnrgxQp24dJYZDhmV4bE3aBtQyt8",
                signer_weight=1,
            ),
            SignerEntry(
                account="rEhxGqkqPPSxQ3P25J66ft5TwpzV14k2de",
                signer_weight=1,
            ),
            SignerEntry(
                account="rf1BiGeXwwQoi8Z2ueFYTEXSwuJYfV2Jpn",
                signer_weight=1,
            ),
            SignerEntry(
                account="rsA2LpzuawewSBQXkiju3YQTMzW13pAAdW",
                signer_weight=1,
            ),
        ]
        with self.assertRaises(XRPLModelException):
            SignerListSet(
                account=_ACCOUNT,
                fee=_FEE,
                sequence=_SEQUENCE,
                signer_quorum=5,
                signer_entries=signer_entries,
            )

    def test_invalid_signer_entries_sender_account(self):
        signer_entries = [SignerEntry(account=_ACCOUNT, signer_weight=5)]
        with self.assertRaises(XRPLModelException):
            SignerListSet(
                account=_ACCOUNT,
                fee=_FEE,
                sequence=_SEQUENCE,
                signer_quorum=3,
                signer_entries=signer_entries,
            )

    def test_invalid_signer_entries_repeat_account(self):
        signer_entries = [
            SignerEntry(
                account="rsA2LpzuawewSBQXkiju3YQTMzW13pAAdW",
                signer_weight=5,
            ),
            SignerEntry(
                account="rsA2LpzuawewSBQXkiju3YQTMzW13pAAdW",
                signer_weight=3,
            ),
        ]
        with self.assertRaises(XRPLModelException):
            SignerListSet(
                account=_ACCOUNT,
                fee=_FEE,
                sequence=_SEQUENCE,
                signer_quorum=7,
                signer_entries=signer_entries,
            )

    def test_invalid_signer_entries_bad_signer_quorum(self):
        with self.assertRaises(XRPLModelException):
            SignerListSet(
                account=_ACCOUNT,
                fee=_FEE,
                sequence=_SEQUENCE,
                signer_quorum=57,
                signer_entries=_SIGNER_ENTRIES_VALID,
            )

    def test_signer_entries_signer_quorum_equal(self):
        tx = SignerListSet(
            account=_ACCOUNT,
            fee=_FEE,
            sequence=_SEQUENCE,
            signer_quorum=4,
            signer_entries=_SIGNER_ENTRIES_VALID,
        )
        self.assertTrue(tx.is_valid())

    def test_signer_entries_signer_quorum_valid(self):
        tx = SignerListSet(
            account=_ACCOUNT,
            fee=_FEE,
            sequence=_SEQUENCE,
            signer_quorum=2,
            signer_entries=_SIGNER_ENTRIES_VALID,
        )
        self.assertTrue(tx.is_valid())
