from unittest import TestCase

from xrpl.models import XRP, XChainBridge, XChainCreateClaimID, XRPLModelException

_ACCOUNT = "r9LqNeG6qHxjeUocjvVki2XR35weJ9mZgQ"
_ACCOUNT2 = "rpZc4mVfWUif9CRoHRKKcmhu1nx2xktxBo"

_ISSUER = "rGWrZyQqhTp9Xu7G5Pkayo7bXjH4k4QYpf"
_GENESIS = "rHb9CJAWyB4rj91VRWn96DkukG4bwdtyTh"

_SOURCE = "rJrRMgiRgrU6hDF4pgu5DXQdWyPbY35ErN"
_SIGNATURE_REWARD = "200"

_XRP_BRIDGE = XChainBridge(
    locking_chain_door=_ACCOUNT,
    locking_chain_issue=XRP(),
    issuing_chain_door=_GENESIS,
    issuing_chain_issue=XRP(),
)


class TestXChainCreateClaimID(TestCase):
    def test_successful(self):
        XChainCreateClaimID(
            account=_ACCOUNT,
            xchain_bridge=_XRP_BRIDGE,
            signature_reward=_SIGNATURE_REWARD,
            other_chain_source=_SOURCE,
        )

    def test_bad_signature_reward(self):
        with self.assertRaises(XRPLModelException):
            XChainCreateClaimID(
                account=_ACCOUNT,
                xchain_bridge=_XRP_BRIDGE,
                signature_reward="hello",
                other_chain_source=_SOURCE,
            )

    def test_bad_other_chain_source(self):
        with self.assertRaises(XRPLModelException):
            XChainCreateClaimID(
                account=_ACCOUNT,
                xchain_bridge=_XRP_BRIDGE,
                signature_reward=_SIGNATURE_REWARD,
                other_chain_source="hello",
            )
