from tests.integration.integration_test_case import IntegrationTestCase
from tests.integration.it_utils import (
    fund_wallet_async,
    sign_and_reliable_submission_async,
    test_async_and_sync,
)
from xrpl.models.amounts import IssuedCurrencyAmount
from xrpl.models.requests import AccountObjects
from xrpl.models.transactions import (
    AccountSet,
    CredentialAccept,
    CredentialCreate,
    OfferCreate,
    Payment,
    PermissionedDomainSet,
    TrustSet,
)
from xrpl.models.transactions.account_set import AccountSetAsfFlag
from xrpl.models.transactions.deposit_preauth import Credential
from xrpl.models.transactions.offer_create import OfferCreateFlag
from xrpl.wallet import Wallet


class TestPermissionedDEX(IntegrationTestCase):
    @test_async_and_sync(globals())
    async def test_permissioned_dex_full_flow(self, client):
        """Full E2E integration test for Permissioned DEX: setup, credential, offer,
        cross, cleanup."""

        # 1. Create issuer (domain owner), wallet1, wallet2
        issuer = Wallet.create()
        await fund_wallet_async(issuer)
        wallet1 = Wallet.create()
        await fund_wallet_async(wallet1)
        wallet2 = Wallet.create()
        await fund_wallet_async(wallet2)

        # 2. Set DefaultRipple on issuer
        account_set = AccountSet(
            account=issuer.address,
            set_flag=AccountSetAsfFlag.ASF_DEFAULT_RIPPLE,
        )
        acctset_resp = await sign_and_reliable_submission_async(
            account_set, issuer, client
        )
        self.assertTrue(acctset_resp.is_successful())

        # 3. Create Credential for wallet1 and wallet2
        credential_type_hex = "50617373706f7274"  # "Passport" in hex
        credential_create_1 = CredentialCreate(
            account=issuer.address,
            subject=wallet1.address,
            credential_type=credential_type_hex,
        )
        await sign_and_reliable_submission_async(credential_create_1, issuer, client)

        credential_create_2 = CredentialCreate(
            account=issuer.address,
            subject=wallet2.address,
            credential_type=credential_type_hex,
        )
        await sign_and_reliable_submission_async(credential_create_2, issuer, client)

        # 4. Create PermissionedDomain
        pdomain_set = PermissionedDomainSet(
            account=issuer.address,
            accepted_credentials=[
                Credential(issuer=issuer.address, credential_type=credential_type_hex)
            ],
        )
        await sign_and_reliable_submission_async(pdomain_set, issuer, client)

        # 5. wallet1 & wallet2 CredentialAccept
        cred_accept_1 = CredentialAccept(
            account=wallet1.address,
            issuer=issuer.address,
            credential_type=credential_type_hex,
        )
        await sign_and_reliable_submission_async(cred_accept_1, wallet1, client)

        cred_accept_2 = CredentialAccept(
            account=wallet2.address,
            issuer=issuer.address,
            credential_type=credential_type_hex,
        )
        await sign_and_reliable_submission_async(cred_accept_2, wallet2, client)

        # 6. Fetch PermissionedDomain ledger object and extract domain_id
        response = await client.request(
            AccountObjects(
                account=issuer.address,
                type="permissioned_domain",
            )
        )
        domain_id = response.result["account_objects"][0]["index"]

        # 7. wallet1: TrustSet for USD
        trust1 = TrustSet(
            account=wallet1.address,
            limit_amount=IssuedCurrencyAmount(
                currency="USD",
                issuer=issuer.address,
                value="10000",
            ),
        )
        resp1 = await sign_and_reliable_submission_async(trust1, wallet1, client)
        self.assertTrue(resp1.is_successful())

        # 8. wallet2: TrustSet for USD
        trust2 = TrustSet(
            account=wallet2.address,
            limit_amount=IssuedCurrencyAmount(
                currency="USD",
                issuer=issuer.address,
                value="10000",
            ),
        )
        resp2 = await sign_and_reliable_submission_async(trust2, wallet2, client)
        self.assertTrue(resp2.is_successful())

        # 9. Fund wallets with USD
        fund_wallets = [wallet1, wallet2]
        for wallet in fund_wallets:
            pay = Payment(
                account=issuer.address,
                amount=IssuedCurrencyAmount(
                    currency="USD",
                    issuer=issuer.address,
                    value="10000",
                ),
                destination=wallet.address,
            )
            pay_resp = await sign_and_reliable_submission_async(pay, issuer, client)
            self.assertTrue(pay_resp.is_successful())

        # 10. wallet1: Permissioned OfferCreate (hybrid example)
        offer_create = OfferCreate(
            account=wallet1.address,
            taker_gets="1000",  # 1000 drops = 0.001 XRP for test, use any value
            taker_pays=IssuedCurrencyAmount(
                currency="USD",
                issuer=issuer.address,
                value="10",
            ),
            flags=OfferCreateFlag.TF_HYBRID,
            domain_id=domain_id,
        )
        offer_resp = await sign_and_reliable_submission_async(
            offer_create, wallet1, client
        )
        self.assertTrue(offer_resp.is_successful())

        # 11. Fetch and validate offer (ledger_entry)
        offers1 = await client.request(
            AccountObjects(account=wallet1.address, type="offer")
        )
        self.assertTrue(
            any(
                obj.get("DomainID") == domain_id
                for obj in offers1.result["account_objects"]
            )
        )

        # 12. wallet2: OfferCreate, crosses previous offer
        offer_cross = OfferCreate(
            account=wallet2.address,
            taker_pays="1000",
            taker_gets=IssuedCurrencyAmount(
                currency="USD",
                issuer=issuer.address,
                value="10",
            ),
            domain_id=domain_id,
        )
        offer_cross_resp = await sign_and_reliable_submission_async(
            offer_cross, wallet2, client
        )
        self.assertTrue(offer_cross_resp.is_successful())

        # 13. Validate both wallets have no open offers (after crossing)
        offers1_after = await client.request(
            AccountObjects(account=wallet1.address, type="offer")
        )
        offers2_after = await client.request(
            AccountObjects(account=wallet2.address, type="offer")
        )
        self.assertFalse(offers1_after.result["account_objects"])
        self.assertFalse(offers2_after.result["account_objects"])
