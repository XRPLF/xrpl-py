from unittest import TestCase

from xrpl.core.binarycodec import decode
from xrpl.models.amounts import IssuedCurrencyAmount, MPTAmount
from xrpl.models.transactions import CheckCreate

_ACCOUNT = "r9LqNeG6qHxjeUocjvVki2XR35weJ9mZgQ"
_DESTINATION = "rf1BiGeXwwQoi8Z2ueFYTEXSwuJYfV2Jpn"


class TestCheckCreate(TestCase):
    def test_valid_send_max(self):
        for send_max in (
            "1000000",
            IssuedCurrencyAmount(currency="USD", issuer=_DESTINATION, value="10"),
            MPTAmount(
                mpt_issuance_id="00000003430427B80BD2D09D36B70B969E12801065F22308",
                value="100",
            ),
        ):
            with self.subTest(send_max=send_max):
                tx = CheckCreate(
                    account=_ACCOUNT,
                    destination=_DESTINATION,
                    send_max=send_max,
                )
                self.assertTrue(tx.is_valid())
                self.assertEqual(decode(tx.blob()), tx.to_xrpl())
                self.assertEqual(CheckCreate.from_xrpl(tx.to_xrpl()), tx)
