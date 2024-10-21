from unittest import TestCase

from xrpl.models import DepositAuthorized


class TestDepositAuthorized(TestCase):
    def test_valid(self):
        req = DepositAuthorized(
            source_account="srcAccount",
            destination_account="dstAccount",
            credentials=[
                "EA85602C1B41F6F1F5E83C0E6B87142FB8957BD209469E4CC347BA2D0C26F66A"
            ],
        )
        self.assertTrue(req.is_valid())
