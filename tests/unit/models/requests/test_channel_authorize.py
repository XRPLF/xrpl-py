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
