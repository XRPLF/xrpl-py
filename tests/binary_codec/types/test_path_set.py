import unittest

import xrpl.binary_codec.types.path_set as path_set
from xrpl.binary_codec.binary_wrappers.binary_parser import BinaryParser


class TestPathSet(unittest.TestCase):
    def test_entire_path_set(self):
        buffer = (
            "1200002200000000240000002E2E00004BF161D4C71AFD498D00000000000000"
            "0000000000000055534400000000000A20B3C85F482532A9578DBB3950B85CA0"
            "6594D168400000000000000A69D446F8038585E9400000000000000000000000"
            "00425443000000000078CA21A6014541AB7B26C3929B9E0CD8C284D61C732103"
            "A4665B1F0B7AE2BCA12E2DB80A192125BBEA660F80E9CEE137BA444C1B0769EC"
            "7447304502205A964536805E35785C659D1F9670D057749AE39668175D6AA75D"
            "25B218FE682E0221009252C0E5DDD5F2712A48F211669DE17B54113918E0D2C2"
            "66F818095E9339D7D3811478CA21A6014541AB7B26C3929B9E0CD8C284D61C83"
            "140A20B3C85F482532A9578DBB3950B85CA06594D1011231585E1F3BD02A15D6"
            "185F8BB9B57CC60DEDDB37C10000000000000000000000004254430000000000"
            "585E1F3BD02A15D6185F8BB9B57CC60DEDDB37C131E4FE687C90257D3D2D694C"
            "8531CDEECBE84F33670000000000000000000000004254430000000000E4FE68"
            "7C90257D3D2D694C8531CDEECBE84F3367310A20B3C85F482532A9578DBB3950"
            "B85CA06594D100000000000000000000000042544300000000000A20B3C85F48"
            "2532A9578DBB3950B85CA06594D1300000000000000000000000005553440000"
            "0000000A20B3C85F482532A9578DBB3950B85CA06594D1FF31585E1F3BD02A15"
            "D6185F8BB9B57CC60DEDDB37C100000000000000000000000042544300000000"
            "00585E1F3BD02A15D6185F8BB9B57CC60DEDDB37C131E4FE687C90257D3D2D69"
            "4C8531CDEECBE84F33670000000000000000000000004254430000000000E4FE"
            "687C90257D3D2D694C8531CDEECBE84F33673115036E2D3F5437A83E5AC3CAEE"
            "34FF2C21DEB618000000000000000000000000425443000000000015036E2D3F"
            "5437A83E5AC3CAEE34FF2C21DEB6183000000000000000000000000055534400"
            "000000000A20B3C85F482532A9578DBB3950B85CA06594D1FF31585E1F3BD02A"
            "15D6185F8BB9B57CC60DEDDB37C1000000000000000000000000425443000000"
            "0000585E1F3BD02A15D6185F8BB9B57CC60DEDDB37C13157180C769B66D942EE"
            "69E6DCC940CA48D82337AD000000000000000000000000425443000000000057"
            "180C769B66D942EE69E6DCC940CA48D82337AD10000000000000000000000000"
            "58525000000000003000000000000000000000000055534400000000000A20B3"
            "C85F482532A9578DBB3950B85CA06594D100`"
        )

        expected_json = [
            [
                {
                    "account": "r9hEDb4xBGRfBCcX3E4FirDWQBAYtpxC8K",
                    "currency": "BTC",
                    "issuer": "r9hEDb4xBGRfBCcX3E4FirDWQBAYtpxC8K",
                },
                {
                    "account": "rM1oqKtfh1zgjdAgbFmaRm3btfGBX25xVo",
                    "currency": "BTC",
                    "issuer": "rM1oqKtfh1zgjdAgbFmaRm3btfGBX25xVo",
                },
                {
                    "account": "rvYAfWj5gh67oV6fW32ZzP3Aw4Eubs59B",
                    "currency": "BTC",
                    "issuer": "rvYAfWj5gh67oV6fW32ZzP3Aw4Eubs59B",
                },
                {
                    "currency": "USD",
                    "issuer": "rvYAfWj5gh67oV6fW32ZzP3Aw4Eubs59B",
                },
            ],
            [
                {
                    "account": "r9hEDb4xBGRfBCcX3E4FirDWQBAYtpxC8K",
                    "currency": "BTC",
                    "issuer": "r9hEDb4xBGRfBCcX3E4FirDWQBAYtpxC8K",
                },
                {
                    "account": "rM1oqKtfh1zgjdAgbFmaRm3btfGBX25xVo",
                    "currency": "BTC",
                    "issuer": "rM1oqKtfh1zgjdAgbFmaRm3btfGBX25xVo",
                },
                {
                    "account": "rpvfJ4mR6QQAeogpXEKnuyGBx8mYCSnYZi",
                    "currency": "BTC",
                    "issuer": "rpvfJ4mR6QQAeogpXEKnuyGBx8mYCSnYZi",
                },
                {
                    "currency": "USD",
                    "issuer": "rvYAfWj5gh67oV6fW32ZzP3Aw4Eubs59B",
                },
            ],
            [
                {
                    "account": "r9hEDb4xBGRfBCcX3E4FirDWQBAYtpxC8K",
                    "currency": "BTC",
                    "issuer": "r9hEDb4xBGRfBCcX3E4FirDWQBAYtpxC8K",
                },
                {
                    "account": "r3AWbdp2jQLXLywJypdoNwVSvr81xs3uhn",
                    "currency": "BTC",
                    "issuer": "r3AWbdp2jQLXLywJypdoNwVSvr81xs3uhn",
                },
                {"currency": "0000000000000000000000005852500000000000"},
                {
                    "currency": "USD",
                    "issuer": "rvYAfWj5gh67oV6fW32ZzP3Aw4Eubs59B",
                },
            ],
        ]

        parser = BinaryParser(buffer)
        pathset = path_set.PathSet.from_parser(parser)
        # pathset2 = path_set.PathSet.from_value
        print(pathset.to_json())
        print(expected_json)
