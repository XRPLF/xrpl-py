from unittest import TestCase

from xrpl.models import (
    XRP,
    IssuedCurrency,
    XChainBridge,
    XChainCreateBridge,
    XRPLModelException,
)

_ACCOUNT = "r9LqNeG6qHxjeUocjvVki2XR35weJ9mZgQ"
_ACCOUNT2 = "rpZc4mVfWUif9CRoHRKKcmhu1nx2xktxBo"
_FEE = "0.00001"
_SEQUENCE = 19048

_ISSUER = "rGWrZyQqhTp9Xu7G5Pkayo7bXjH4k4QYpf"

_GENESIS = "rHb9CJAWyB4rj91VRWn96DkukG4bwdtyTh"


class TestXChainCreateBridge(TestCase):
    def test_successful_xrp_xrp_bridge(self):
        bridge = XChainBridge(
            locking_chain_door=_ACCOUNT,
            locking_chain_issue=XRP(),
            issuing_chain_door=_GENESIS,
            issuing_chain_issue=XRP(),
        )
        XChainCreateBridge(
            account=_ACCOUNT,
            fee=_FEE,
            sequence=_SEQUENCE,
            xchain_bridge=bridge,
            signature_reward="200",
            min_account_create_amount="1000000",
        )

    def test_successful_iou_iou_bridge(self):
        bridge = XChainBridge(
            locking_chain_door=_ACCOUNT,
            locking_chain_issue=IssuedCurrency(currency="USD", issuer=_ISSUER),
            issuing_chain_door=_ACCOUNT2,
            issuing_chain_issue=IssuedCurrency(currency="USD", issuer=_ACCOUNT2),
        )
        XChainCreateBridge(
            account=_ACCOUNT,
            fee=_FEE,
            sequence=_SEQUENCE,
            xchain_bridge=bridge,
            signature_reward="200",
        )

    def test_same_door_accounts(self):
        bridge = XChainBridge(
            locking_chain_door=_ACCOUNT,
            locking_chain_issue=IssuedCurrency(currency="USD", issuer=_ISSUER),
            issuing_chain_door=_ACCOUNT,
            issuing_chain_issue=IssuedCurrency(currency="USD", issuer=_ACCOUNT),
        )
        with self.assertRaises(XRPLModelException):
            XChainCreateBridge(
                account=_ACCOUNT,
                fee=_FEE,
                sequence=_SEQUENCE,
                xchain_bridge=bridge,
                signature_reward="200",
            )

    def test_xrp_iou_bridge(self):
        bridge = XChainBridge(
            locking_chain_door=_ACCOUNT,
            locking_chain_issue=XRP(),
            issuing_chain_door=_ACCOUNT,
            issuing_chain_issue=IssuedCurrency(currency="USD", issuer=_ACCOUNT),
        )
        with self.assertRaises(XRPLModelException):
            XChainCreateBridge(
                account=_ACCOUNT,
                fee=_FEE,
                sequence=_SEQUENCE,
                xchain_bridge=bridge,
                signature_reward="200",
            )

    def test_iou_xrp_bridge(self):
        bridge = XChainBridge(
            locking_chain_door=_ACCOUNT,
            locking_chain_issue=IssuedCurrency(currency="USD", issuer=_ISSUER),
            issuing_chain_door=_ACCOUNT,
            issuing_chain_issue=XRP(),
        )
        with self.assertRaises(XRPLModelException):
            XChainCreateBridge(
                account=_ACCOUNT,
                fee=_FEE,
                sequence=_SEQUENCE,
                xchain_bridge=bridge,
                signature_reward="200",
            )

    def test_account_not_in_bridge(self):
        bridge = XChainBridge(
            locking_chain_door=_ACCOUNT,
            locking_chain_issue=XRP(),
            issuing_chain_door=_ACCOUNT2,
            issuing_chain_issue=XRP(),
        )
        with self.assertRaises(XRPLModelException):
            XChainCreateBridge(
                account=_GENESIS,
                fee=_FEE,
                sequence=_SEQUENCE,
                xchain_bridge=bridge,
                signature_reward="200",
            )

    def test_iou_iou_min_account_create_amount(self):
        bridge = XChainBridge(
            locking_chain_door=_ACCOUNT,
            locking_chain_issue=IssuedCurrency(currency="USD", issuer=_ISSUER),
            issuing_chain_door=_ACCOUNT2,
            issuing_chain_issue=IssuedCurrency(currency="USD", issuer=_ACCOUNT2),
        )
        with self.assertRaises(XRPLModelException):
            XChainCreateBridge(
                account=_ACCOUNT,
                fee=_FEE,
                sequence=_SEQUENCE,
                xchain_bridge=bridge,
                signature_reward="200",
                min_account_create_amount="1000000",
            )

    def test_invalid_signature_reward(self):
        bridge = XChainBridge(
            locking_chain_door=_ACCOUNT,
            locking_chain_issue=XRP(),
            issuing_chain_door=_GENESIS,
            issuing_chain_issue=XRP(),
        )
        with self.assertRaises(XRPLModelException):
            XChainCreateBridge(
                account=_ACCOUNT,
                fee=_FEE,
                sequence=_SEQUENCE,
                xchain_bridge=bridge,
                signature_reward="hello",
                min_account_create_amount="1000000",
            )

    def test_invalid_min_account_create_amount(self):
        bridge = XChainBridge(
            locking_chain_door=_ACCOUNT,
            locking_chain_issue=XRP(),
            issuing_chain_door=_GENESIS,
            issuing_chain_issue=XRP(),
        )
        with self.assertRaises(XRPLModelException):
            XChainCreateBridge(
                account=_ACCOUNT,
                fee=_FEE,
                sequence=_SEQUENCE,
                xchain_bridge=bridge,
                signature_reward="-200",
                min_account_create_amount="hello",
            )
