from unittest import TestCase

from xrpl.models.exceptions import XRPLModelException
from xrpl.models.transactions.vault_delete import VaultDelete
from xrpl.utils import str_to_hex

_ACCOUNT = "rsA2LpzuawewSBQXkiju3YQTMzW13pAAdW"
_VAULT_ID = "B982D2AAEF6014E6BE3194D939865453D56D16FF7081BB1D0ED865C708ABCEEE"


class TestVaultDelete(TestCase):
    def test_valid(self):
        tx = VaultDelete(
            account=_ACCOUNT,
            vault_id=_VAULT_ID,
        )
        self.assertTrue(tx.is_valid())

    def test_valid_with_memo_data(self):
        tx = VaultDelete(
            account=_ACCOUNT,
            vault_id=_VAULT_ID,
            memo_data=str_to_hex("A" * 256),
        )
        self.assertTrue(tx.is_valid())
        self.assertEqual(tx.to_xrpl()["MemoData"], str_to_hex("A" * 256))

    def test_long_memo_data_field(self):
        with self.assertRaises(XRPLModelException) as e:
            VaultDelete(
                account=_ACCOUNT,
                vault_id=_VAULT_ID,
                memo_data=str_to_hex("A" * 257),
            )
        self.assertEqual(
            e.exception.args[0],
            str(
                {
                    "memo_data": "MemoData must be an even-length hex string less "
                    "than 256 bytes (alternatively, 512 hex characters)."
                }
            ),
        )

    def test_non_hex_memo_data_field(self):
        # Non-hex characters pass a length-only check but crash MemoData encoding.
        with self.assertRaises(XRPLModelException) as e:
            VaultDelete(
                account=_ACCOUNT,
                vault_id=_VAULT_ID,
                memo_data="GG",
            )
        self.assertEqual(
            e.exception.args[0],
            str(
                {
                    "memo_data": "MemoData must be an even-length hex string less "
                    "than 256 bytes (alternatively, 512 hex characters)."
                }
            ),
        )

    def test_odd_length_memo_data_field(self):
        # An odd number of hex characters fails bytes.fromhex during encoding.
        with self.assertRaises(XRPLModelException) as e:
            VaultDelete(
                account=_ACCOUNT,
                vault_id=_VAULT_ID,
                memo_data="ABC",
            )
        self.assertEqual(
            e.exception.args[0],
            str(
                {
                    "memo_data": "MemoData must be an even-length hex string less "
                    "than 256 bytes (alternatively, 512 hex characters)."
                }
            ),
        )

    def test_invalid_vault_id_field(self):
        with self.assertRaises(XRPLModelException) as e:
            VaultDelete(
                account=_ACCOUNT,
                vault_id="0",
            )
        self.assertEqual(
            e.exception.args[0],
            str(
                {
                    "vault_id": "Invalid vault ID: Length must be 32 characters "
                    "(64 hex characters)."
                }
            ),
        )
