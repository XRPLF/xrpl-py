from unittest import TestCase

from xrpl.models.amounts import IssuedCurrencyAmount
from xrpl.models.exceptions import XRPLModelException
from xrpl.models.transactions import AMMBid

_ACCOUNT = "r9LqNeG6qHxjeUocjvVki2XR35weJ9mZgQ"
_AMM_HASH = "24BA86F99302CF124AB27311C831F5BFAA72C4625DDA65B7EDF346A60CC19883"
_AUTH_ACCOUNTS = [
    "rNZdsTBP5tH1M6GHC6bTreHAp6ouP8iZSh",
    "rfpFv97Dwu89FTyUwPjtpZBbuZxTqqgTmH",
    "rzzYHPGb8Pa64oqxCzmuffm122bitq3Vb",
    "rhwxHxaHok86fe4LykBom1jSJ3RYQJs1h4",
]
_LPTOKENS_CURRENCY = "5475B6C930B7BDD81CDA8FBA5CED962B11218E5A"
_LPTOKENS_ISSUER = "r3628pXjRqfw5zfwGfhSusjZTvE3BoxEBw"


class TestAMMBid(TestCase):
    def test_auth_accounts_length_error(self):
        auth_accounts = _AUTH_ACCOUNTS.copy()
        auth_accounts.append("r3X6noRsvaLapAKCG78zAtWcbhB3sggS1s")
        with self.assertRaises(XRPLModelException):
            AMMBid(
                account=_ACCOUNT,
                amm_hash=_AMM_HASH,
                auth_accounts=auth_accounts,
            )

    def test_to_xrpl(self):
        tx = AMMBid(
            account=_ACCOUNT,
            amm_hash=_AMM_HASH,
            min_slot_price=IssuedCurrencyAmount(
                currency=_LPTOKENS_CURRENCY,
                issuer=_LPTOKENS_ISSUER,
                value="25",
            ),
            max_slot_price=IssuedCurrencyAmount(
                currency=_LPTOKENS_CURRENCY,
                issuer=_LPTOKENS_ISSUER,
                value="35",
            ),
            auth_accounts=_AUTH_ACCOUNTS,
        )
        expected = {
            "Account": "r9LqNeG6qHxjeUocjvVki2XR35weJ9mZgQ",
            "AMMHash": _AMM_HASH,
            "MinSlotPrice": {
                "currency": "5475B6C930B7BDD81CDA8FBA5CED962B11218E5A",
                "issuer": "r3628pXjRqfw5zfwGfhSusjZTvE3BoxEBw",
                "value": "25",
            },
            "MaxSlotPrice": {
                "currency": "5475B6C930B7BDD81CDA8FBA5CED962B11218E5A",
                "issuer": "r3628pXjRqfw5zfwGfhSusjZTvE3BoxEBw",
                "value": "35",
            },
            "AuthAccounts": _AUTH_ACCOUNTS,
            "TransactionType": "AMMBid",
            "SigningPubKey": "",
            "Flags": 0,
        }
        self.assertEqual(tx.to_xrpl(), expected)
