"""Integration tests for the LendingProtocolV1_1 amendment features.

These exercise the client-model additions that are part of the merged
``LendingProtocolV1_1`` amendment:

* Close-ended vaults on ``VaultCreate`` -- the ``VaultKind`` /
  ``SubscriptionDate`` / ``RedemptionDate`` fields (XLS-587 / #587).
* The ``MemoData`` field on ``VaultDelete`` (#470).
* ``CredentialIDs`` on ``VaultWithdraw`` for withdrawing from a
  permissioned-domain-gated vault (#538).

They require a ``rippled`` node with the ``LendingProtocolV1_1`` (and its
prerequisite ``SingleAssetVault``) amendment enabled (see
``.ci-config/xrpld.cfg``).
"""

from datetime import datetime, timezone

from tests.integration.integration_test_case import IntegrationTestCase
from tests.integration.it_utils import (
    fund_wallet_async,
    sign_and_reliable_submission_async,
    test_async_and_sync,
)
from xrpl.models.currencies.xrp import XRP
from xrpl.models.requests.account_objects import AccountObjects, AccountObjectType
from xrpl.models.response import ResponseStatus
from xrpl.models.transactions.credential_accept import CredentialAccept
from xrpl.models.transactions.credential_create import CredentialCreate
from xrpl.models.transactions.permissioned_domain_set import (
    Credential,
    PermissionedDomainSet,
)
from xrpl.models.transactions.vault_create import (
    VaultCreate,
    VaultCreateFlag,
    VaultKind,
    WithdrawalPolicy,
)
from xrpl.models.transactions.vault_delete import VaultDelete
from xrpl.models.transactions.vault_deposit import VaultDeposit
from xrpl.models.transactions.vault_withdraw import VaultWithdraw
from xrpl.utils import datetime_to_ripple_time, str_to_hex
from xrpl.wallet import Wallet


class TestLendingProtocolV1_1(IntegrationTestCase):
    @test_async_and_sync(globals())
    async def test_close_ended_vault_create(self, client):
        """#587: create a close-ended vault with subscription/redemption dates."""
        vault_owner = Wallet.create()
        await fund_wallet_async(vault_owner)

        # A close-ended vault requires a future subscription date and a
        # redemption date at least kMinInvestmentPeriod (60s) later.
        now = datetime_to_ripple_time(datetime.now(timezone.utc))
        subscription_date = now + 300
        redemption_date = subscription_date + 3600

        response = await sign_and_reliable_submission_async(
            VaultCreate(
                account=vault_owner.address,
                asset=XRP(),
                assets_maximum="1000",
                withdrawal_policy=(
                    WithdrawalPolicy.VAULT_STRATEGY_FIRST_COME_FIRST_SERVE
                ),
                vault_kind=VaultKind.CLOSED,
                subscription_date=subscription_date,
                redemption_date=redemption_date,
            ),
            vault_owner,
            client,
        )
        self.assertEqual(response.status, ResponseStatus.SUCCESS)
        self.assertEqual(response.result["engine_result"], "tesSUCCESS")

        account_objects_response = await client.request(
            AccountObjects(account=vault_owner.address, type=AccountObjectType.VAULT)
        )
        self.assertEqual(len(account_objects_response.result["account_objects"]), 1)

    @test_async_and_sync(globals())
    async def test_vault_delete_with_memo_data(self, client):
        """#470: VaultDelete accepts an arbitrary MemoData field."""
        vault_owner = Wallet.create()
        await fund_wallet_async(vault_owner)

        response = await sign_and_reliable_submission_async(
            VaultCreate(
                account=vault_owner.address,
                asset=XRP(),
                assets_maximum="1000",
                withdrawal_policy=(
                    WithdrawalPolicy.VAULT_STRATEGY_FIRST_COME_FIRST_SERVE
                ),
            ),
            vault_owner,
            client,
        )
        self.assertEqual(response.status, ResponseStatus.SUCCESS)
        self.assertEqual(response.result["engine_result"], "tesSUCCESS")

        account_objects_response = await client.request(
            AccountObjects(account=vault_owner.address, type=AccountObjectType.VAULT)
        )
        self.assertEqual(len(account_objects_response.result["account_objects"]), 1)
        vault_id = account_objects_response.result["account_objects"][0]["index"]

        # Delete the (empty) vault, supplying the new MemoData field.
        response = await sign_and_reliable_submission_async(
            VaultDelete(
                account=vault_owner.address,
                vault_id=vault_id,
                memo_data=str_to_hex("closing vault"),
            ),
            vault_owner,
            client,
        )
        self.assertEqual(response.status, ResponseStatus.SUCCESS)
        self.assertEqual(response.result["engine_result"], "tesSUCCESS")

        # The vault should be gone.
        account_objects_response = await client.request(
            AccountObjects(account=vault_owner.address, type=AccountObjectType.VAULT)
        )
        self.assertEqual(len(account_objects_response.result["account_objects"]), 0)

    @test_async_and_sync(globals())
    async def test_vault_withdraw_with_credential_ids(self, client):
        """#538: withdraw from a domain-gated vault authorized by credentials."""
        issuer = Wallet.create()
        await fund_wallet_async(issuer)
        vault_owner = Wallet.create()
        await fund_wallet_async(vault_owner)
        depositor = Wallet.create()
        await fund_wallet_async(depositor)

        # Issue a credential to the depositor and have them accept it.
        cred_type = str_to_hex("VaultAccess")
        await sign_and_reliable_submission_async(
            CredentialCreate(
                account=issuer.address,
                subject=depositor.address,
                credential_type=cred_type,
            ),
            issuer,
            client,
        )
        credential_accept_response = await sign_and_reliable_submission_async(
            CredentialAccept(
                account=depositor.address,
                issuer=issuer.address,
                credential_type=cred_type,
            ),
            depositor,
            client,
        )
        self.assertEqual(
            credential_accept_response.result["engine_result"], "tesSUCCESS"
        )

        credential_objects = await client.request(
            AccountObjects(account=depositor.address, type=AccountObjectType.CREDENTIAL)
        )
        credential_id = credential_objects.result["account_objects"][0]["index"]

        # A PermissionedDomain accepting that credential.
        await sign_and_reliable_submission_async(
            PermissionedDomainSet(
                account=issuer.address,
                accepted_credentials=[
                    Credential(credential_type=cred_type, issuer=issuer.address)
                ],
            ),
            issuer,
            client,
        )
        pd_objects = await client.request(
            AccountObjects(
                account=issuer.address, type=AccountObjectType.PERMISSIONED_DOMAIN
            )
        )
        domain_id = pd_objects.result["account_objects"][0]["index"]

        # A private, domain-gated vault.
        response = await sign_and_reliable_submission_async(
            VaultCreate(
                account=vault_owner.address,
                asset=XRP(),
                assets_maximum="10000",
                domain_id=domain_id,
                withdrawal_policy=(
                    WithdrawalPolicy.VAULT_STRATEGY_FIRST_COME_FIRST_SERVE
                ),
                flags=VaultCreateFlag.TF_VAULT_PRIVATE,
            ),
            vault_owner,
            client,
        )
        self.assertEqual(response.result["engine_result"], "tesSUCCESS")
        vault_objects = await client.request(
            AccountObjects(account=vault_owner.address, type=AccountObjectType.VAULT)
        )
        vault_id = vault_objects.result["account_objects"][0]["index"]

        # The credentialed depositor can deposit into the private vault.
        response = await sign_and_reliable_submission_async(
            VaultDeposit(account=depositor.address, vault_id=vault_id, amount="1000"),
            depositor,
            client,
        )
        self.assertEqual(response.result["engine_result"], "tesSUCCESS")

        # ...and withdraw, authorizing the withdrawal with the credential.
        response = await sign_and_reliable_submission_async(
            VaultWithdraw(
                account=depositor.address,
                vault_id=vault_id,
                amount="100",
                credential_ids=[credential_id],
            ),
            depositor,
            client,
        )
        self.assertEqual(response.status, ResponseStatus.SUCCESS)
        self.assertEqual(response.result["engine_result"], "tesSUCCESS")
