from unittest import IsolatedAsyncioTestCase
from unittest.mock import AsyncMock, patch

from xrpl.asyncio.transaction.main import _calculate_fee_per_transaction_type
from xrpl.models.transactions import (
    ConfidentialMPTClawback,
    ConfidentialMPTConvert,
    ConfidentialMPTConvertBack,
    ConfidentialMPTMergeInbox,
    ConfidentialMPTSend,
)

_BASE_FEE = 10
# rippled charges base_fee * (1 + kConfidentialFeeMultiplier); multiplier == 9.
_EXPECTED_CONFIDENTIAL_FEE = str(_BASE_FEE * 10)

_ACCOUNT = "rsA2LpzuawewSBQXkiju3YQTMzW13pAAdW"
_HOLDER = "rN7n3473SaZBCG4dFL83w7a1RXtXtbk2D9"
_ISSUANCE_ID = "0000012FFD9EE5DA93AC614B4DB94D7E0FCE415CA51BED47"
# ConfidentialMPTClawback is issuer-only, so its issuance ID must embed
# _ACCOUNT's AccountID (204288D2..09711) as the issuer.
_CLAWBACK_ISSUANCE_ID = "0000012F204288D2E47F8EF6C99BCC457966320D12409711"
_CIPHERTEXT = "A" * 132
_COMMITMENT = "B" * 66


class TestConfidentialFee(IsolatedAsyncioTestCase):
    async def _fee_for(self, transaction):
        with patch(
            "xrpl.asyncio.transaction.main.get_fee",
            new=AsyncMock(return_value=str(_BASE_FEE)),
        ):
            return await _calculate_fee_per_transaction_type(transaction, AsyncMock())

    async def test_merge_inbox_fee(self):
        tx = ConfidentialMPTMergeInbox(
            account=_ACCOUNT, mptoken_issuance_id=_ISSUANCE_ID
        )
        self.assertEqual(await self._fee_for(tx), _EXPECTED_CONFIDENTIAL_FEE)

    async def test_clawback_fee(self):
        tx = ConfidentialMPTClawback(
            account=_ACCOUNT,
            holder=_HOLDER,
            mptoken_issuance_id=_CLAWBACK_ISSUANCE_ID,
            mpt_amount=1000,
            zk_proof="A" * 128,
        )
        self.assertEqual(await self._fee_for(tx), _EXPECTED_CONFIDENTIAL_FEE)

    async def test_send_fee(self):
        tx = ConfidentialMPTSend(
            account=_ACCOUNT,
            destination=_HOLDER,
            mptoken_issuance_id=_ISSUANCE_ID,
            sender_encrypted_amount=_CIPHERTEXT,
            destination_encrypted_amount=_CIPHERTEXT,
            issuer_encrypted_amount=_CIPHERTEXT,
            zk_proof="C" * 1892,
            amount_commitment=_COMMITMENT,
            balance_commitment=_COMMITMENT,
        )
        self.assertEqual(await self._fee_for(tx), _EXPECTED_CONFIDENTIAL_FEE)

    async def test_convert_fee(self):
        tx = ConfidentialMPTConvert(
            account=_ACCOUNT,
            mptoken_issuance_id=_ISSUANCE_ID,
            mpt_amount=1000,
            holder_encrypted_amount=_CIPHERTEXT,
            issuer_encrypted_amount=_CIPHERTEXT,
            blinding_factor="B" * 64,
        )
        self.assertEqual(await self._fee_for(tx), _EXPECTED_CONFIDENTIAL_FEE)

    async def test_convert_back_fee(self):
        tx = ConfidentialMPTConvertBack(
            account=_ACCOUNT,
            mptoken_issuance_id=_ISSUANCE_ID,
            mpt_amount=1000,
            holder_encrypted_amount=_CIPHERTEXT,
            issuer_encrypted_amount=_CIPHERTEXT,
            blinding_factor="C" * 64,
            balance_commitment=_COMMITMENT,
            zk_proof="D" * 1632,
        )
        self.assertEqual(await self._fee_for(tx), _EXPECTED_CONFIDENTIAL_FEE)

    async def test_confidential_fee_includes_multisigner_surcharge(self):
        # base * (1 + 9) + base * signers_count
        tx = ConfidentialMPTMergeInbox(
            account=_ACCOUNT, mptoken_issuance_id=_ISSUANCE_ID
        )
        with patch(
            "xrpl.asyncio.transaction.main.get_fee",
            new=AsyncMock(return_value=str(_BASE_FEE)),
        ):
            fee = await _calculate_fee_per_transaction_type(
                tx, AsyncMock(), signers_count=2
            )
        self.assertEqual(fee, str(_BASE_FEE * 10 + _BASE_FEE * 2))
