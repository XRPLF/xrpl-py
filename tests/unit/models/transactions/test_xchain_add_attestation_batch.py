from unittest import TestCase

from xrpl.models import XRP, XChainAddAttestationBatch, XChainBridge, XRPLModelException
from xrpl.models.transactions.xchain_add_attestation_batch import (
    XChainAttestationBatch,
    XChainClaimAttestationBatchElement,
    XChainCreateAccountAttestationBatchElement,
)

_ACCOUNT = "r9LqNeG6qHxjeUocjvVki2XR35weJ9mZgQ"
_ACCOUNT2 = "rpZc4mVfWUif9CRoHRKKcmhu1nx2xktxBo"
_ACCOUNT3 = "r9cZA1mLK5R5Am25ArfXFmqgNwjZgnfk59"

_REWARD_ACCOUNT = "rGWrZyQqhTp9Xu7G5Pkayo7bXjH4k4QYpf"

_GENESIS = "rHb9CJAWyB4rj91VRWn96DkukG4bwdtyTh"

_XRP_BRIDGE = XChainBridge(
    locking_chain_door=_ACCOUNT,
    locking_chain_issue=XRP(),
    issuing_chain_door=_GENESIS,
    issuing_chain_issue=XRP(),
)

_CLAIM_ATTESTATION = XChainClaimAttestationBatchElement(
    account=_ACCOUNT2,
    amount="10000000",
    attestation_reward_account=_REWARD_ACCOUNT,
    public_key="ED3CC1BBD0952A60088E89FA502921895FC81FBD79CAE9109A8FE2D23659AD5D56",
    signature="616263",
    was_locking_chain_send=0,
    xchain_claim_id="2",
)

_ACCOUNT_CREATE_ATTESTATION = XChainCreateAccountAttestationBatchElement(
    account=_ACCOUNT2,
    amount="10000000",
    attestation_reward_account=_REWARD_ACCOUNT,
    destination=_ACCOUNT3,
    signature_reward="200",
    public_key="ED3CC1BBD0952A60088E89FA502921895FC81FBD79CAE9109A8FE2D23659AD5D56",
    signature="616263",
    was_locking_chain_send=0,
    xchain_account_create_count="2",
)


class TestXChainAddAttestationBatch(TestCase):
    def test_successful(self):
        XChainAddAttestationBatch(
            account=_ACCOUNT,
            xchain_attestation_batch=XChainAttestationBatch(
                xchain_bridge=_XRP_BRIDGE,
                xchain_claim_attestation_batch=[_CLAIM_ATTESTATION],
                xchain_create_account_attestation_batch=[_ACCOUNT_CREATE_ATTESTATION],
            ),
        )

    def test_too_many_attestations(self):
        with self.assertRaises(XRPLModelException):
            XChainAddAttestationBatch(
                account=_ACCOUNT,
                xchain_attestation_batch=XChainAttestationBatch(
                    xchain_bridge=_XRP_BRIDGE,
                    xchain_claim_attestation_batch=[_CLAIM_ATTESTATION] * 4,
                    xchain_create_account_attestation_batch=[
                        _ACCOUNT_CREATE_ATTESTATION
                    ]
                    * 5,
                ),
            )
