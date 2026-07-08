from unittest import TestCase

from xrpl.models.requests import SignAndSubmit
from xrpl.models.transactions import AccountSet, AccountSetAsfFlag

_ACCOUNT = "r9LqNeG6qHxjeUocjvVki2XR35weJ9mZgQ"
_FEE = "0.00001"
_SEQUENCE = 19048
_DOMAIN = "asjcsodafsaid0f9asdfasdf"
_TRANSACTION = AccountSet(
    account=_ACCOUNT,
    fee=_FEE,
    set_flag=AccountSetAsfFlag.ASF_DISALLOW_XRP,
    domain=_DOMAIN,
    sequence=_SEQUENCE,
)

_SECRET = "randomsecretkey"
_SEED = "randomsecretseedforakey"
_SEED_HEX = "EACEB081770D8ADE216C85445DD6FB002C6B5A2930F2DECE006DA18150CB18F6"
_PASSPHRASE = "mytopsecretpassphrasethatwillneverbehacked"


class TestSignAndSubmit(TestCase):
    def test_sensitive_fields_HIDDEN_in_repr(self):
        """Regression test for issue #992: secret, seed, seed_hex, and
        passphrase must never appear in repr() / str() output, since those
        surfaces commonly feed logs and error-reporting pipelines. The raw
        values must still round-trip through to_dict() so the RPC payload
        is unchanged."""
        for field, value in [
            ("secret", _SECRET),
            ("seed", _SEED),
            ("seed_hex", _SEED_HEX),
            ("passphrase", _PASSPHRASE),
        ]:
            request = SignAndSubmit(transaction=_TRANSACTION, **{field: value})
            self.assertNotIn(value, repr(request), f"{field} leaked via repr")
            self.assertNotIn(value, str(request), f"{field} leaked via str")
            self.assertIn("-HIDDEN-", repr(request))
            self.assertIn("-HIDDEN-", str(request))
            self.assertEqual(request.to_dict()[field], value)

    def test_non_sensitive_fields_appear_in_repr(self):
        """Redaction must not over-mask: ordinary fields must still appear in
        repr() with their real values, and the overall shape must match the
        standard dataclass format `ClassName(field=value, ...)`."""
        request = SignAndSubmit(
            transaction=_TRANSACTION,
            seed=_SEED,
            offline=True,
            fee_mult_max=42,
        )
        rendered = repr(request)
        self.assertTrue(rendered.startswith("SignAndSubmit("))
        self.assertTrue(rendered.endswith(")"))
        # Non-sensitive scalar fields render with their real values
        self.assertIn("offline=True", rendered)
        self.assertIn("fee_mult_max=42", rendered)
        # Nested transaction is rendered (not replaced by a placeholder)
        self.assertIn(f"account='{_ACCOUNT}'", rendered)
        self.assertIn(f"domain='{_DOMAIN}'", rendered)
        # None-valued sensitive fields are rendered as None, not -HIDDEN-
        self.assertIn("secret=None", rendered)
        self.assertIn("passphrase=None", rendered)
