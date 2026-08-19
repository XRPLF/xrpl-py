import unittest

from xrpl.models.exceptions import XRPLModelException
from xrpl.models.transactions.account_set import AccountSet
from xrpl.models.transactions.account_set import AccountSetAsfFlag
from xrpl.models.transactions.account_set import AccountSetFlag


class TestAccountSet(unittest.TestCase):
    def test_tx_invalid_transfer_rate_greater_than_max(self):
        with self.assertRaises(XRPLModelException) as err:
            AccountSet(
                account="rHb9CJAWyB4rj91VRWn96DkukG4bwdtyTh",
                clear_flag=AccountSetAsfFlag.ASF_ALLOW_TRUSTLINE_CLAWBACK,
                domain="eee1865f2068c323ed13e569d12f8a77db2249d1be0dd0ed8afed6fd23f0221a",
                email_hash="1280cff9a097213f011d9162251999e1",
                flags=AccountSetFlag.TF_ALLOW_XRP,
                message_key="AAAAA",
                set_flag=AccountSetAsfFlag.ASF_ACCOUNT_TXN_ID,
                tick_size=3,
                transfer_rate=2000000001,
                wallet_locator="2561865f2068c323ed13e569d12f8a77db2249d1be0dd0ed8afed6fd23f0221a",
                wallet_size=5,
            )
        self.assertIsNotNone(err.exception.args[0])

    def test_tx_invalid_tick_size_greater_than_max(self):
        with self.assertRaises(XRPLModelException) as err:
            AccountSet(
                account="rHb9CJAWyB4rj91VRWn96DkukG4bwdtyTh",
                clear_flag=AccountSetAsfFlag.ASF_ALLOW_TRUSTLINE_CLAWBACK,
                domain="eee1865f2068c323ed13e569d12f8a77db2249d1be0dd0ed8afed6fd23f0221a",
                email_hash="1280cff9a097213f011d9162251999e1",
                flags=AccountSetFlag.TF_ALLOW_XRP,
                message_key="AAAAA",
                set_flag=AccountSetAsfFlag.ASF_ACCOUNT_TXN_ID,
                tick_size=16,
                transfer_rate=1000000000,
                wallet_locator="2561865f2068c323ed13e569d12f8a77db2249d1be0dd0ed8afed6fd23f0221a",
                wallet_size=5,
            )
        self.assertIsNotNone(err.exception.args[0])

    def test_tx_invalid_transfer_rate_less_than_min(self):
        with self.assertRaises(XRPLModelException) as err:
            AccountSet(
                account="rHb9CJAWyB4rj91VRWn96DkukG4bwdtyTh",
                clear_flag=AccountSetAsfFlag.ASF_ALLOW_TRUSTLINE_CLAWBACK,
                domain="eee1865f2068c323ed13e569d12f8a77db2249d1be0dd0ed8afed6fd23f0221a",
                email_hash="1280cff9a097213f011d9162251999e1",
                flags=AccountSetFlag.TF_ALLOW_XRP,
                message_key="AAAAA",
                set_flag=AccountSetAsfFlag.ASF_ACCOUNT_TXN_ID,
                tick_size=3,
                transfer_rate=999999999,
                wallet_locator="2561865f2068c323ed13e569d12f8a77db2249d1be0dd0ed8afed6fd23f0221a",
                wallet_size=5,
            )
        self.assertIsNotNone(err.exception.args[0])

    def test_tx_invalid_tick_size_less_than_min(self):
        with self.assertRaises(XRPLModelException) as err:
            AccountSet(
                account="rHb9CJAWyB4rj91VRWn96DkukG4bwdtyTh",
                clear_flag=AccountSetAsfFlag.ASF_ALLOW_TRUSTLINE_CLAWBACK,
                domain="eee1865f2068c323ed13e569d12f8a77db2249d1be0dd0ed8afed6fd23f0221a",
                email_hash="1280cff9a097213f011d9162251999e1",
                flags=AccountSetFlag.TF_ALLOW_XRP,
                message_key="AAAAA",
                set_flag=AccountSetAsfFlag.ASF_ACCOUNT_TXN_ID,
                tick_size=2,
                transfer_rate=1000000000,
                wallet_locator="2561865f2068c323ed13e569d12f8a77db2249d1be0dd0ed8afed6fd23f0221a",
                wallet_size=5,
            )
        self.assertIsNotNone(err.exception.args[0])

    def test_tx_invalid_missing_required_param_account(self):
        with self.assertRaises(XRPLModelException) as err:
            AccountSet(
                clear_flag=AccountSetAsfFlag.ASF_ALLOW_TRUSTLINE_CLAWBACK,
                domain="eee1865f2068c323ed13e569d12f8a77db2249d1be0dd0ed8afed6fd23f0221a",
                email_hash="1280cff9a097213f011d9162251999e1",
                flags=AccountSetFlag.TF_ALLOW_XRP,
                message_key="AAAAA",
                set_flag=AccountSetAsfFlag.ASF_ACCOUNT_TXN_ID,
                tick_size=3,
                transfer_rate=1000000000,
                wallet_locator="2561865f2068c323ed13e569d12f8a77db2249d1be0dd0ed8afed6fd23f0221a",
                wallet_size=5,
            )
        self.assertIsNotNone(err.exception.args[0])

    def test_tx_invalid_duplicate_set_flag_and_clear_flag(self):
        with self.assertRaises(XRPLModelException) as err:
            AccountSet(
                account="rHb9CJAWyB4rj91VRWn96DkukG4bwdtyTh",
                clear_flag=AccountSetAsfFlag.ASF_ALLOW_TRUSTLINE_CLAWBACK,
                domain="eee1865f2068c323ed13e569d12f8a77db2249d1be0dd0ed8afed6fd23f0221a",
                email_hash="1280cff9a097213f011d9162251999e1",
                flags=AccountSetFlag.TF_ALLOW_XRP,
                message_key="AAAAA",
                set_flag=AccountSetAsfFlag.ASF_ALLOW_TRUSTLINE_CLAWBACK,
                tick_size=3,
                transfer_rate=1000000000,
                wallet_locator="2561865f2068c323ed13e569d12f8a77db2249d1be0dd0ed8afed6fd23f0221a",
                wallet_size=5,
            )
        self.assertIsNotNone(err.exception.args[0])

    def test_tx_invalid_domain_too_long(self):
        with self.assertRaises(XRPLModelException) as err:
            AccountSet(
                account="rHb9CJAWyB4rj91VRWn96DkukG4bwdtyTh",
                clear_flag=AccountSetAsfFlag.ASF_ALLOW_TRUSTLINE_CLAWBACK,
                domain="eee1865f2068c323ed13e569d12f8a77db2249d1be0dd0ed8afed6fd23f0221aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
                email_hash="1280cff9a097213f011d9162251999e1",
                flags=AccountSetFlag.TF_ALLOW_XRP,
                message_key="AAAAA",
                set_flag=AccountSetAsfFlag.ASF_ACCOUNT_TXN_ID,
                tick_size=3,
                transfer_rate=1000000000,
                wallet_locator="2561865f2068c323ed13e569d12f8a77db2249d1be0dd0ed8afed6fd23f0221a",
                wallet_size=5,
            )
        self.assertIsNotNone(err.exception.args[0])

    def test_tx_invalid_present_nftoken_minter_on_missing_asf_authorized_nftoken_minter(
        self,
    ):
        with self.assertRaises(XRPLModelException) as err:
            AccountSet(
                account="rHb9CJAWyB4rj91VRWn96DkukG4bwdtyTh",
                clear_flag=AccountSetAsfFlag.ASF_ALLOW_TRUSTLINE_CLAWBACK,
                domain="eee1865f2068c323ed13e569d12f8a77db2249d1be0dd0ed8afed6fd23f0221a",
                email_hash="1280cff9a097213f011d9162251999e1",
                flags=AccountSetFlag.TF_ALLOW_XRP,
                message_key="AAAAA",
                set_flag=AccountSetAsfFlag.ASF_ACCOUNT_TXN_ID,
                tick_size=3,
                transfer_rate=1000000000,
                wallet_locator="2561865f2068c323ed13e569d12f8a77db2249d1be0dd0ed8afed6fd23f0221a",
                wallet_size=5,
                nftoken_minter="AAAAA",
            )
        self.assertIsNotNone(err.exception.args[0])

    def test_tx_valid_special_value_tick_size(self):
        tx = AccountSet(
            account="rHb9CJAWyB4rj91VRWn96DkukG4bwdtyTh",
            clear_flag=AccountSetAsfFlag.ASF_ALLOW_TRUSTLINE_CLAWBACK,
            domain="eee1865f2068c323ed13e569d12f8a77db2249d1be0dd0ed8afed6fd23f0221a",
            email_hash="1280cff9a097213f011d9162251999e1",
            flags=AccountSetFlag.TF_ALLOW_XRP,
            message_key="AAAAA",
            set_flag=AccountSetAsfFlag.ASF_ACCOUNT_TXN_ID,
            tick_size=0,
            transfer_rate=1000000000,
            wallet_locator="2561865f2068c323ed13e569d12f8a77db2249d1be0dd0ed8afed6fd23f0221a",
            wallet_size=5,
        )
        self.assertTrue(tx.is_valid())

    def test_tx_valid_special_value_transfer_rate(self):
        tx = AccountSet(
            account="rHb9CJAWyB4rj91VRWn96DkukG4bwdtyTh",
            clear_flag=AccountSetAsfFlag.ASF_ALLOW_TRUSTLINE_CLAWBACK,
            domain="eee1865f2068c323ed13e569d12f8a77db2249d1be0dd0ed8afed6fd23f0221a",
            email_hash="1280cff9a097213f011d9162251999e1",
            flags=AccountSetFlag.TF_ALLOW_XRP,
            message_key="AAAAA",
            set_flag=AccountSetAsfFlag.ASF_ACCOUNT_TXN_ID,
            tick_size=3,
            transfer_rate=0,
            wallet_locator="2561865f2068c323ed13e569d12f8a77db2249d1be0dd0ed8afed6fd23f0221a",
            wallet_size=5,
        )
        self.assertTrue(tx.is_valid())

    def test_tx_invalid_domain_not_lower_case(self):
        with self.assertRaises(XRPLModelException) as err:
            AccountSet(
                account="rHb9CJAWyB4rj91VRWn96DkukG4bwdtyTh",
                clear_flag=AccountSetAsfFlag.ASF_ALLOW_TRUSTLINE_CLAWBACK,
                domain="EEE1865F2068C323ED13E569D12F8A77DB2249D1BE0DD0ED8AFED6FD23F0221A",
                email_hash="1280cff9a097213f011d9162251999e1",
                flags=AccountSetFlag.TF_ALLOW_XRP,
                message_key="AAAAA",
                set_flag=AccountSetAsfFlag.ASF_ACCOUNT_TXN_ID,
                tick_size=3,
                transfer_rate=1000000000,
                wallet_locator="2561865f2068c323ed13e569d12f8a77db2249d1be0dd0ed8afed6fd23f0221a",
                wallet_size=5,
            )
        self.assertIsNotNone(err.exception.args[0])

    def test_tx_invalid_account_is_not_xrp_account(self):
        with self.assertRaises(XRPLModelException) as err:
            AccountSet(
                account="G5h7Dk92LmXqZtP3NvB8YrCfJ0W1AoUE",
                clear_flag=AccountSetAsfFlag.ASF_ALLOW_TRUSTLINE_CLAWBACK,
                domain="eee1865f2068c323ed13e569d12f8a77db2249d1be0dd0ed8afed6fd23f0221a",
                email_hash="1280cff9a097213f011d9162251999e1",
                flags=AccountSetFlag.TF_ALLOW_XRP,
                message_key="AAAAA",
                set_flag=AccountSetAsfFlag.ASF_ACCOUNT_TXN_ID,
                tick_size=3,
                transfer_rate=1000000000,
                wallet_locator="2561865f2068c323ed13e569d12f8a77db2249d1be0dd0ed8afed6fd23f0221a",
                wallet_size=5,
            )
        self.assertIsNotNone(err.exception.args[0])

    def test_tx_valid_transaction(self):
        tx = AccountSet(
            account="rHb9CJAWyB4rj91VRWn96DkukG4bwdtyTh",
            clear_flag=AccountSetAsfFlag.ASF_ALLOW_TRUSTLINE_CLAWBACK,
            domain="eee1865f2068c323ed13e569d12f8a77db2249d1be0dd0ed8afed6fd23f0221a",
            email_hash="1280cff9a097213f011d9162251999e1",
            flags=AccountSetFlag.TF_ALLOW_XRP,
            message_key="AAAAA",
            set_flag=AccountSetAsfFlag.ASF_ACCOUNT_TXN_ID,
            tick_size=3,
            transfer_rate=1000000000,
            wallet_locator="2561865f2068c323ed13e569d12f8a77db2249d1be0dd0ed8afed6fd23f0221a",
            wallet_size=5,
        )
        self.assertTrue(tx.is_valid())
