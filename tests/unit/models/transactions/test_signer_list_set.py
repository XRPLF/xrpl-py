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

    def test_max_signer_entries_above_8_below_32(self):
        signers = [
            "rBFBipte4nAQCTsRxd2czwvSurhCpAf4X6",
            "r3ijUH32iiy9tYNj3rD7hKWYjy1BFUxngm",
            "rpwq8vi4Mn3L5kDJmb8Mg59CanPFPzMCnj",
            "rB72Gzqfejai46nkA4HaKYBHwAnn2yUoT4",
            "rGqsJSAW71pCfUwDD5m52bLw69RzFg6kMW",
            "rs8smPRA31Ym4mGxb1wzgwxtU5eVK82Gyk",
            "rLrugpGxzezUQLDh7Jv1tZpouuV4MQLbU9",
            "rUQ6zLXQdh1jJLGwMXp9P8rgi42kwuafzs",
            "rMjY8sPdfxsyRrnVKQcutxr4mTHNXy9dEF",
        ]
        signer_entries = []
        for acc in signers:
            signer_entries.append(
                SignerEntry(
                    account=acc,
                    signer_weight=1,
                )
            )

        tx = SignerListSet(
            account=_ACCOUNT,
            fee=_FEE,
            sequence=_SEQUENCE,
            signer_quorum=9,
            signer_entries=signer_entries,
        )
        self.assertTrue(tx.is_valid())

    def test_max_signer_entries_exceeded(self):
        signers = [
            "rBFBipte4nAQCTsRxd2czwvSurhCpAf4X6",
            "r3ijUH32iiy9tYNj3rD7hKWYjy1BFUxngm",
            "rpwq8vi4Mn3L5kDJmb8Mg59CanPFPzMCnj",
            "rB72Gzqfejai46nkA4HaKYBHwAnn2yUoT4",
            "rGqsJSAW71pCfUwDD5m52bLw69RzFg6kMW",
            "rs8smPRA31Ym4mGxb1wzgwxtU5eVK82Gyk",
            "rLrugpGxzezUQLDh7Jv1tZpouuV4MQLbU9",
            "rUQ6zLXQdh1jJLGwMXp9P8rgi42kwuafzs",
            "rMjY8sPdfxsyRrnVKQcutxr4mTHNXy9dEF",
            "rUaxYLeFGm6SmMoa2WCqLKSyHwJyvaQmeG",
            "r9wUfeVtqMfqrcDTfCpNYbNZvs5q9M9Rpo",
            "rQncVNak5kvJGPUFa6fuKH7t8Usjs7Np1c",
            "rnwbSSnPbVbUzuBa4etkeYrfy5v7SyhtPu",
            "rDXh5D3t48MdBJyXByXq47k5P8Kuf1758B",
            "rh1D4jd2mAiqUPHfAZ2cY9Nbfa3kAkaQXP",
            "r9T129tXgtnyfGoLeS35c2HctaZAZSQoCH",
            "rUd2uKsyCWfJP7Ve36mKoJbNCA7RYThnYk",
            "r326x8PaAFtnaH7uoxaKrcDWuwpeHn4wDa",
            "rpN3mkXkYhfNadcXPrY4LniM1KpM3egyQM",
            "rsPKbR155hz1zrA4pSJp5Y2fxasZAatcHb",
            "rsyWFLaEKTpaoSJusjpcDvGexuHCwMnqss",
            "rUbc5RXfyF81oLDMgd3d7jpY9YMNMZG4XN",
            "rGpYHM88BZe1iVKFHm5xiWYYxR74oxJEXf",
            "rPsetWAtR1KxDtxzgHjRMD7Rc87rvXk5nD",
            "rwSeNhL6Hi34igr12mCr61jY42psfTkWTq",
            "r46Mygy98qjkDhVB6qs4sBnqaf7FPiA2vU",
            "r4s8GmeYN4CiwVate1nMUvwMQbundqf5cW",
            "rKAr4dQWDYG8cG2hSwJUVp4ry4WNaWiNgp",
            "rPWXRLp1vqeUHEH3WiSKuyo9GM9XhaENQU",
            "rPgmdBdRKGmndxNEYxUrrsYCZaS6go9RvW",
            "rPDJZ9irzgwKRKScfEmuJMvUgrqZAJNCbL",
            "rDuU2uSXMfEaoxN1qW8sj7aUNFLGEn3Hr2",
            "rsbjSjA4TCB9gtm7x7SrWbZHB6g4tt9CGU",
        ]
        signer_entries = []
        for acc in signers:
            signer_entries.append(
                SignerEntry(
                    account=acc,
                    signer_weight=1,
                )
            )

        with self.assertRaises(XRPLModelException):
            SignerListSet(
                account=_ACCOUNT,
                fee=_FEE,
                sequence=_SEQUENCE,
                signer_quorum=33,
                signer_entries=signer_entries,
            )

    def test_signer_entries_with_wallet_locator(self):
        signer_entries = [
            SignerEntry(
                account="rBFBipte4nAQCTsRxd2czwvSurhCpAf4X6",
                signer_weight=1,
                wallet_locator="CAFECAFECAFECAFECAFECAFECAFECAFECAFECAFECAFECAFECAFECAF"
                "ECAFECAFE",
            ),
            SignerEntry(
                account="r3ijUH32iiy9tYNj3rD7hKWYjy1BFUxngm",
                signer_weight=1,
            ),
            SignerEntry(
                account="rpwq8vi4Mn3L5kDJmb8Mg59CanPFPzMCnj",
                signer_weight=1,
                wallet_locator="0000000000000000000000000000000000000000000000000000000"
                "0DEADBEEF",
            ),
        ]
        tx = SignerListSet(
            account=_ACCOUNT,
            fee=_FEE,
            sequence=_SEQUENCE,
            signer_quorum=3,
            signer_entries=signer_entries,
        )
        self.assertTrue(tx.is_valid())

    def test_signer_entries_with_invalid_wallet_locator(self):
        signer_entries = [
            SignerEntry(
                account="rBFBipte4nAQCTsRxd2czwvSurhCpAf4X6",
                signer_weight=1,
                wallet_locator="not_valid",
            ),
            SignerEntry(
                account="r3ijUH32iiy9tYNj3rD7hKWYjy1BFUxngm",
                signer_weight=1,
            ),
        ]
        with self.assertRaises(XRPLModelException):
            SignerListSet(
                account=_ACCOUNT,
                fee=_FEE,
                sequence=_SEQUENCE,
                signer_quorum=2,
                signer_entries=signer_entries,
            )
