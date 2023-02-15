from unittest import TestCase

from xrpl.models import (
    XRP,
    IssuedCurrency,
    XChainAccountCreateCommit,
    XChainBridge,
    XRPLModelException,
)

_ACCOUNT = "r9LqNeG6qHxjeUocjvVki2XR35weJ9mZgQ"
_ACCOUNT2 = "rpZc4mVfWUif9CRoHRKKcmhu1nx2xktxBo"

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


class TestXChainAccountCreateCommit(TestCase):
    def test_successful(self):
        XChainAccountCreateCommit(
            account=_ACCOUNT,
            xchain_bridge=_XRP_BRIDGE,
            signature_reward="200",
            destination=_ACCOUNT2,
            amount="1000000",
        )

    def test_bad_signature_reward(self):
        with self.assertRaises(XRPLModelException):
            XChainAccountCreateCommit(
                account=_ACCOUNT,
                xchain_bridge=_XRP_BRIDGE,
                signature_reward="hello",
                destination=_ACCOUNT2,
                amount="1000000",
            )

    def test_bad_amount(self):
        with self.assertRaises(XRPLModelException):
            XChainAccountCreateCommit(
                account=_ACCOUNT,
                xchain_bridge=_XRP_BRIDGE,
                signature_reward="200",
                destination=_ACCOUNT2,
                amount="hello",
            )
