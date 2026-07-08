from unittest import TestCase

from xrpl.models.exceptions import XRPLModelException
from xrpl.models.requests import ChannelAuthorize

_CHANNEL_ID = "5DB01B7FFED6B67E6B0414DED11E051D2EE2B7619CE0EAA6286D67A3A4D5BDB3"
_AMOUNT = "10000"
_DUMMY_STRING = "loremipsem"


class TestChannelAuthorize(TestCase):
    def test_has_secret_only_is_valid(self):
        request = ChannelAuthorize(
            channel_id=_CHANNEL_ID,
            amount=_AMOUNT,
            secret=_DUMMY_STRING,
        )
        self.assertTrue(request.is_valid())

    def test_has_seed_only_is_valid(self):
        request = ChannelAuthorize(
            channel_id=_CHANNEL_ID,
            amount=_AMOUNT,
            seed=_DUMMY_STRING,
        )
        self.assertTrue(request.is_valid())

    def test_has_seed_hex_only_is_valid(self):
        request = ChannelAuthorize(
            channel_id=_CHANNEL_ID,
            amount=_AMOUNT,
            seed_hex=_DUMMY_STRING,
        )
        self.assertTrue(request.is_valid())

    def test_has_passphrase_only_is_valid(self):
        request = ChannelAuthorize(
            channel_id=_CHANNEL_ID,
            amount=_AMOUNT,
            passphrase=_DUMMY_STRING,
        )
        self.assertTrue(request.is_valid())

    def test_has_no_signing_method_is_invalid(self):
        with self.assertRaises(XRPLModelException):
            ChannelAuthorize(
                channel_id=_CHANNEL_ID,
                amount=_AMOUNT,
            )

    def test_has_multiple_signing_methods_is_invalid(self):
        with self.assertRaises(XRPLModelException):
            ChannelAuthorize(
                channel_id=_CHANNEL_ID,
                amount=_AMOUNT,
                passphrase=_DUMMY_STRING,
                seed_hex=_DUMMY_STRING,
            )

    def test_sensitive_fields_HIDDEN_in_repr(self):
        """Regression test for issue #992: secret, seed, seed_hex, and
        passphrase must never appear in repr() / str() output, since those
        surfaces commonly feed logs and error-reporting pipelines. The raw
        values must still round-trip through to_dict() so the RPC payload
        is unchanged."""
        for field in ["secret", "seed", "seed_hex", "passphrase"]:
            request = ChannelAuthorize(
                channel_id=_CHANNEL_ID,
                amount=_AMOUNT,
                **{field: _DUMMY_STRING},
            )
            self.assertNotIn(_DUMMY_STRING, repr(request), f"{field} leaked via repr")
            self.assertNotIn(_DUMMY_STRING, str(request), f"{field} leaked via str")
            self.assertIn("-HIDDEN-", repr(request))
            self.assertIn("-HIDDEN-", str(request))
            self.assertEqual(request.to_dict()[field], _DUMMY_STRING)

    def test_non_sensitive_fields_appear_in_repr(self):
        """Redaction must not over-mask: ordinary fields must still appear in
        repr() with their real values, and the overall shape must match the
        standard dataclass format `ClassName(field=value, ...)`."""
        request = ChannelAuthorize(
            channel_id=_CHANNEL_ID,
            amount=_AMOUNT,
            seed=_DUMMY_STRING,
        )
        rendered = repr(request)
        self.assertTrue(rendered.startswith("ChannelAuthorize("))
        self.assertTrue(rendered.endswith(")"))
        self.assertIn(f"channel_id='{_CHANNEL_ID}'", rendered)
        self.assertIn(f"amount='{_AMOUNT}'", rendered)
        # None-valued sensitive fields are rendered as None, not -HIDDEN-
        self.assertIn("secret=None", rendered)
        self.assertIn("passphrase=None", rendered)
