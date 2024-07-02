from unittest import TestCase

from xrpl.models.amounts import IssuedCurrencyAmount
from xrpl.models.currencies import XRP, IssuedCurrency
from xrpl.models.exceptions import XRPLModelException
from xrpl.models.transactions import AMMBid, AuthAccount

_ACCOUNT = "r9LqNeG6qHxjeUocjvVki2XR35weJ9mZgQ"
_ASSET = XRP()
_ASSET2 = IssuedCurrency(currency="ETH", issuer="rpGtkFRXhgVaBzC5XCR7gyE2AZN5SN3SEW")
_AUTH_ACCOUNTS = [
    AuthAccount(
        account="rNZdsTBP5tH1M6GHC6bTreHAp6ouP8iZSh",
    ),
    AuthAccount(
        account="rfpFv97Dwu89FTyUwPjtpZBbuZxTqqgTmH",
    ),
    AuthAccount(
        account="rzzYHPGb8Pa64oqxCzmuffm122bitq3Vb",
    ),
    AuthAccount(
        account="rhwxHxaHok86fe4LykBom1jSJ3RYQJs1h4",
    ),
]
_LPTOKEN_CURRENCY = "5475B6C930B7BDD81CDA8FBA5CED962B11218E5A"
_LPTOKEN_ISSUER = "r3628pXjRqfw5zfwGfhSusjZTvE3BoxEBw"


class TestAMMBid(TestCase):
    def test_tx_valid(self):
        tx = AMMBid(
            account=_ACCOUNT,
            asset=_ASSET,
            asset2=_ASSET2,
            bid_min=IssuedCurrencyAmount(
                currency=_LPTOKEN_CURRENCY,
                issuer=_LPTOKEN_ISSUER,
                value="25",
            ),
            bid_max=IssuedCurrencyAmount(
                currency=_LPTOKEN_CURRENCY,
                issuer=_LPTOKEN_ISSUER,
                value="35",
            ),
            auth_accounts=_AUTH_ACCOUNTS,
        )
        self.assertTrue(tx.is_valid())

    def test_auth_accounts_length_error(self):
        auth_accounts = _AUTH_ACCOUNTS.copy()
        auth_accounts.append(
            AuthAccount(
                account="r3X6noRsvaLapAKCG78zAtWcbhB3sggS1s",
            ),
        )
        with self.assertRaises(XRPLModelException) as error:
            AMMBid(
                account=_ACCOUNT,
                asset=_ASSET,
                asset2=_ASSET2,
                auth_accounts=auth_accounts,
            )
        self.assertEqual(
            error.exception.args[0],
            "{'auth_accounts': 'Length must not be greater than 4'}",
        )
