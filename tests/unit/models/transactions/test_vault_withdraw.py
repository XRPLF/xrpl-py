from unittest import TestCase

from xrpl.models.amounts import IssuedCurrencyAmount
from xrpl.models.exceptions import XRPLModelException
from xrpl.models.transactions.vault_withdraw import VaultWithdraw

_ACCOUNT = "rsA2LpzuawewSBQXkiju3YQTMzW13pAAdW"
_VAULT_ID = "B982D2AAEF6014E6BE3194D939865453D56D16FF7081BB1D0ED865C708ABCEEE"
_DESTINATION = "rf1BiGeXwwQoi8Z2ueFYTEXSwuJYfV2Jpn"


class TestVaultWithdraw(TestCase):
    def test_valid(self):
        tx = VaultWithdraw(
            account=_ACCOUNT,
            vault_id=_VAULT_ID,
            amount=IssuedCurrencyAmount(currency="USD", issuer=_ACCOUNT, value="100"),
        )
        self.assertTrue(tx.is_valid())

    def test_valid_with_destination_tag(self):
        tx = VaultWithdraw(
            account=_ACCOUNT,
            vault_id=_VAULT_ID,
            amount=IssuedCurrencyAmount(currency="USD", issuer=_ACCOUNT, value="100"),
            destination=_DESTINATION,
            destination_tag=3000,
        )
        self.assertTrue(tx.is_valid())

    def test_invalid_vault_id_field(self):
        with self.assertRaises(XRPLModelException) as e:
            VaultWithdraw(
                account=_ACCOUNT,
                amount=IssuedCurrencyAmount(
                    currency="USD", issuer=_ACCOUNT, value="100"
                ),
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
