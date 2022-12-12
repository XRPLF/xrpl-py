from unittest import TestCase

from xrpl.models import (
    XRP,
    IssuedCurrency,
    XChainBridge,
    XChainModifyBridge,
    XRPLModelException,
)

_ACCOUNT = "r9LqNeG6qHxjeUocjvVki2XR35weJ9mZgQ"
_ACCOUNT2 = "rpZc4mVfWUif9CRoHRKKcmhu1nx2xktxBo"
_FEE = "0.00001"
_SEQUENCE = 19048

_ISSUER = "rGWrZyQqhTp9Xu7G5Pkayo7bXjH4k4QYpf"

_GENESIS = "rHb9CJAWyB4rj91VRWn96DkukG4bwdtyTh"

_XRP_BRIDGE = XChainBridge(
    locking_chain_door=_ACCOUNT,
    locking_chain_issue=XRP(),
    issuing_chain_door=_GENESIS,
    issuing_chain_issue=XRP(),
)

_IOU_BRIDGE = XChainBridge(
    locking_chain_door=_ACCOUNT,
    locking_chain_issue=IssuedCurrency(currency="USD", issuer=_ISSUER),
    issuing_chain_door=_ACCOUNT2,
    issuing_chain_issue=IssuedCurrency(currency="USD", issuer=_ACCOUNT2),
)


class TestXChainModifyBridge(TestCase):
    def test_successful_modify_bridge(self):
        XChainModifyBridge(
            account=_ACCOUNT,
            fee=_FEE,
            sequence=_SEQUENCE,
            xchain_bridge=_XRP_BRIDGE,
            signature_reward="200",
            min_account_create_amount="1000000",
        )

    def test_successful_modify_bridge_only_signature_reward(self):
        XChainModifyBridge(
            account=_ACCOUNT,
            fee=_FEE,
            sequence=_SEQUENCE,
            xchain_bridge=_IOU_BRIDGE,
            signature_reward="200",
        )

    def test_successful_modify_bridge_only_min_account_create_amount(self):
        XChainModifyBridge(
            account=_ACCOUNT,
            fee=_FEE,
            sequence=_SEQUENCE,
            xchain_bridge=_XRP_BRIDGE,
            min_account_create_amount="1000000",
        )

    def test_modify_bridge_empty(self):
        with self.assertRaises(XRPLModelException):
            XChainModifyBridge(
                account=_ACCOUNT,
                fee=_FEE,
                sequence=_SEQUENCE,
                xchain_bridge=_IOU_BRIDGE,
            )

    def test_account_not_in_bridge(self):
        with self.assertRaises(XRPLModelException):
            XChainModifyBridge(
                account=_ACCOUNT2,
                fee=_FEE,
                sequence=_SEQUENCE,
                xchain_bridge=_XRP_BRIDGE,
                signature_reward="200",
            )

    def test_iou_iou_min_account_create_amount(self):
        with self.assertRaises(XRPLModelException):
            XChainModifyBridge(
                account=_ACCOUNT,
                fee=_FEE,
                sequence=_SEQUENCE,
                xchain_bridge=_IOU_BRIDGE,
                min_account_create_amount="1000000",
            )

    def test_invalid_signature_reward(self):
        with self.assertRaises(XRPLModelException):
            XChainModifyBridge(
                account=_ACCOUNT,
                fee=_FEE,
                sequence=_SEQUENCE,
                xchain_bridge=_XRP_BRIDGE,
                signature_reward="hello",
                min_account_create_amount="1000000",
            )

    def test_invalid_min_account_create_amount(self):
        with self.assertRaises(XRPLModelException):
            XChainModifyBridge(
                account=_ACCOUNT,
                fee=_FEE,
                sequence=_SEQUENCE,
                xchain_bridge=_XRP_BRIDGE,
                signature_reward="200",
                min_account_create_amount="hello",
            )
