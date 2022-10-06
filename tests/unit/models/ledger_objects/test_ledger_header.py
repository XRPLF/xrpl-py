from unittest import TestCase

from xrpl.models.ledger.ledger import Ledger

HEADER = {
    "account_hash": "CDE3C9D978C7CBE78A40B4DA4D1FCC0D44C84B0E91981B3761B05B8F6C9C0A42",
    "close_flags": 0,
    "close_time": 718221910,
    "close_time_human": "2022-Oct-04 18:05:10.000000000 UTC",
    "close_time_resolution": 10,
    "closed": True,
    "ledger_hash": "4616A47627427444FF812A33FF43206323FB130C828C68B361AA2B0C3EE44B58",
    "ledger_index": "74838077",
    "parent_close_time": 718221902,
    "parent_hash": "A8616DB44675A302929AFF74814C65850AE2E1C3D4332CD64BEC7B6966B7C68F",
    "total_coins": "99989265714191880",
    "transaction_hash": "8D534B19426824E1AD2B2542FF4E30E3416F5C9198FBFB984A137866193"
    "68803",
}


class Test(TestCase):
    def test(self):
        ledger = Ledger.from_dict(HEADER)
        ledger_dict = ledger.to_dict()
        self.assertEqual(HEADER, ledger_dict)
