from unittest import TestCase

from xrpl.models import (
    XRP,
    IssuedCurrency,
    IssuedCurrencyAmount,
    XChainBridge,
    XChainClaim,
    XRPLModelException,
)

_ACCOUNT = "r9LqNeG6qHxjeUocjvVki2XR35weJ9mZgQ"
_ACCOUNT2 = "rpZc4mVfWUif9CRoHRKKcmhu1nx2xktxBo"
_FEE = "0.00001"
_SEQUENCE = 19048

_ISSUER = "rGWrZyQqhTp9Xu7G5Pkayo7bXjH4k4QYpf"
_GENESIS = "rHb9CJAWyB4rj91VRWn96DkukG4bwdtyTh"

_DESTINATION = "rJrRMgiRgrU6hDF4pgu5DXQdWyPbY35ErN"
_CLAIM_ID = 3
_XRP_AMOUNT = "123456789"
_IOU_AMOUNT = IssuedCurrencyAmount(currency="USD", issuer=_ISSUER, value="123")

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


class TestXChainClaim(TestCase):
    def test_successful_claim_xrp(self):
        XChainClaim(
            account=_ACCOUNT,
            fee=_FEE,
            sequence=_SEQUENCE,
            xchain_bridge=_XRP_BRIDGE,
            xchain_claim_id=_CLAIM_ID,
            destination=_DESTINATION,
            amount=_XRP_AMOUNT,
        )

    def test_successful_claim_iou(self):
        XChainClaim(
            account=_ACCOUNT,
            fee=_FEE,
            sequence=_SEQUENCE,
            xchain_bridge=_IOU_BRIDGE,
            xchain_claim_id=_CLAIM_ID,
            destination=_DESTINATION,
            amount=_IOU_AMOUNT,
        )

    def test_successful_claim_destination_tag(self):
        XChainClaim(
            account=_ACCOUNT,
            fee=_FEE,
            sequence=_SEQUENCE,
            xchain_bridge=_XRP_BRIDGE,
            xchain_claim_id=_CLAIM_ID,
            destination=_DESTINATION,
            destination_tag=12345,
            amount=_XRP_AMOUNT,
        )

    def test_successful_claim_str_claim_id(self):
        XChainClaim(
            account=_ACCOUNT,
            fee=_FEE,
            sequence=_SEQUENCE,
            xchain_bridge=_XRP_BRIDGE,
            xchain_claim_id=str(_CLAIM_ID),
            destination=_DESTINATION,
            amount=_XRP_AMOUNT,
        )

    def test_xrp_bridge_iou_amount(self):
        with self.assertRaises(XRPLModelException):
            XChainClaim(
                account=_ACCOUNT,
                fee=_FEE,
                sequence=_SEQUENCE,
                xchain_bridge=_XRP_BRIDGE,
                xchain_claim_id=_CLAIM_ID,
                destination=_DESTINATION,
                amount=_IOU_AMOUNT,
            )

    def test_iou_bridge_xrp_amount(self):
        with self.assertRaises(XRPLModelException):
            XChainClaim(
                account=_ACCOUNT,
                fee=_FEE,
                sequence=_SEQUENCE,
                xchain_bridge=_IOU_BRIDGE,
                xchain_claim_id=_CLAIM_ID,
                destination=_DESTINATION,
                amount=_XRP_AMOUNT,
            )
