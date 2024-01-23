from unittest import TestCase

from xrpl.models import IssuedCurrencyAmount
from xrpl.models.auth_account import AuthAccount
from xrpl.models.currencies.issued_currency import IssuedCurrency
from xrpl.models.currencies.xrp import XRP
from xrpl.models.ledger_objects import (
    AMM,
    DID,
    AccountRoot,
    Amendments,
    Check,
    DepositPreauth,
    DirectoryNode,
    DisabledValidator,
    Escrow,
    FeeSettings,
    LedgerHashes,
    Majority,
    NegativeUNL,
    NFToken,
    NFTokenOffer,
    NFTokenPage,
    Offer,
    PayChannel,
    RippleState,
    SignerEntry,
    SignerList,
    Ticket,
)
from xrpl.models.ledger_objects.amm import AuctionSlot, VoteEntry
from xrpl.models.ledger_objects.bridge import Bridge
from xrpl.models.xchain_bridge import XChainBridge

account_root_json = {
    "account": "rf1BiGeXwwQoi8Z2ueFYTEXSwuJYfV2Jpn",
    "account_txn_id": "0D5FB50FA65C9FE1538FD7E398FFFE9D190"
    "8DFA4576D8D7A020040686F93C77D",
    "balance": "148446663",
    "domain": "6D64756F31332E636F6D",
    "email_hash": "98B4375E1D753E5B91627516F6D70977",
    "flags": 8388608,
    "ledger_entry_type": "AccountRoot",
    "message_key": "0000000000000000000000070000000300",
    "owner_count": 3,
    "nftoken_minter": "rHello",
    "previous_txn_id": "0D5FB50FA65C9FE1538FD7E398FFFE9D1908DFA4576D8D7A0200"
    "40686F93C77D",
    "previous_txn_lgr_seq": 14091160,
    "sequence": 336,
    "transfer_rate": 1004999999,
    "index": "13F1A95D7AAB7108D5CE7EEAF504B2894B8C674E6D68499076441C4837282BF8",
}

amendment_json = {
    "majorities": [
        {
            "majority": {
                "amendment": "1562511F573A19AE9BD103B5D6B9E01B3B46805AEC5D3C4805C902B51"
                "4399146",
                "close_time": 535589001,
            }
        }
    ],
    "amendments": [
        "42426C4D4F1009EE67080A9B7965B44656D7714D104A72F9B4369F97ABF044EE",
        "4C97EBA926031A7CF7D7B36FDE3ED66DDA5421192D63DE53FFB46E43B9DC8373",
        "6781F8368C4771B83E8B821D88F580202BCB4228075297B19E4FDC5233F1EFDC",
        "740352F2412A9909880C23A559FCECEDA3BE2126FED62FC7660D628A06927F11",
    ],
    "flags": 0,
    "ledger_entry_type": "Amendments",
    "index": "7DB0788C020F02780A673DC74757F23823FA3014C1866E72CC4CD8B226CD6EF4",
}

amm_json = {
    "account": "rE54zDvgnghAoPopCgvtiqWNq3dU5y836S",
    "asset": {"currency": "XRP"},
    "asset2": {"currency": "TST", "issuer": "rP9jPyP5kyvFRb6ZiRghAGw5u8SGAmU4bd"},
    "auction_slot": {
        "account": "rJVUeRqDFNs2xqA7ncVE6ZoAhPUoaJJSQm",
        "auth_accounts": [
            {"auth_account": {"account": "rMKXGCbJ5d8LbrqthdG46q3f969MVK2Qeg"}},
            {"auth_account": {"account": "rBepJuTLFJt3WmtLXYAxSjtBWAeQxVbncv"}},
        ],
        "discounted_fee": 0,
        "expiration": 721870180,
        "price": {
            "currency": "039C99CD9AB0B70B32ECDA51EAAE471625608EA2",
            "issuer": "rE54zDvgnghAoPopCgvtiqWNq3dU5y836S",
            "value": "0.8696263565463045",
        },
    },
    "lptoken_balance": {
        "currency": "039C99CD9AB0B70B32ECDA51EAAE471625608EA2",
        "issuer": "rE54zDvgnghAoPopCgvtiqWNq3dU5y836S",
        "value": "71150.53584131501",
    },
    "trading_fee": 600,
    "vote_slots": [
        {
            "vote_entry": {
                "account": "rJVUeRqDFNs2xqA7ncVE6ZoAhPUoaJJSQm",
                "trading_fee": 600,
                "vote_weight": 100000,
            }
        }
    ],
    "flags": 0,
    "ledger_entry_type": "AMM",
}

bridge_json = {
    "account": "r3nCVTbZGGYoWvZ58BcxDmiMUU7ChMa1eC",
    "flags": 0,
    "ledger_entry_type": "Bridge",
    "min_account_create_amount": "2000000000",
    "owner_node": "0",
    "previous_txn_id": "67A8A1B36C1B97BE3AAB6B19CB3A3069034877DE917FD1A71919EAE7548E56"
    "36",
    "previous_txn_lgr_seq": 102,
    "signature_reward": "204",
    "xchain_account_claim_count": "0",
    "xchain_account_create_count": "0",
    "xchain_bridge": {
        "issuing_chain_door": "rHb9CJAWyB4rj91VRWn96DkukG4bwdtyTh",
        "issuing_chain_issue": {"currency": "XRP"},
        "locking_chain_door": "r3nCVTbZGGYoWvZ58BcxDmiMUU7ChMa1eC",
        "locking_chain_issue": {"currency": "XRP"},
    },
    "xchain_claim_id": "1",
    "index": "9F2C9E23343852036AFD323025A8506018ABF9D4DBAA746D61BF1CFB5C297D10",
}

check_json = {
    "account": "rUn84CUYbNjRoTQ6mSW7BVJPSVJNLb1QLo",
    "destination": "rfkE1aSy9G8Upk4JssnwBxhEv5p4mn2KTy",
    "destination_node": "0000000000000000",
    "destination_tag": 1,
    "expiration": 570113521,
    "flags": 0,
    "invoice_id": "46060241FABCF692D4D934BA2A6C4427CD4279083E38C77CBE642243E43BE291",
    "ledger_entry_type": "Check",
    "owner_node": "0000000000000000",
    "previous_txn_id": "5463C6E08862A1FAE5EDAC12D70ADB16546A1F67"
    "4930521295BC082494B62924",
    "previous_txn_lgr_seq": 6,
    "send_max": "100000000",
    "sequence": 2,
    "index": "49647F0D748DC3FE26BDACBC57F251AADEFFF391403EC9BF87C97F67E9977FB0",
}

deposit_preauth_json = {
    "ledger_entry_type": "DepositPreauth",
    "account": "rsUiUMpnrgxQp24dJYZDhmV4bE3aBtQyt8",
    "authorize": "rEhxGqkqPPSxQ3P25J66ft5TwpzV14k2de",
    "flags": 0,
    "owner_node": "0000000000000000",
    "previous_txn_id": "3E8964D5A86B3CD6B9ECB33310D4E073D64C865A5B866200"
    "AD2B7E29F8326702",
    "previous_txn_lgr_seq": 7,
    "index": "4A255038CC3ADCC1A9C91509279B59908251728D0DAADB248FFE297D0F7E068C",
}

did_json = {
    "account": "rpfqJrXg5uidNo2ZsRhRY6TiF1cvYmV9Fg",
    "did_document": "646F63",
    "data": "617474657374",
    "flags": 0,
    "ledger_entry_type": "DID",
    "owner_node": "0",
    "previous_txn_id": "A4C15DA185E6092DF5954FF62A1446220C61A5F60F0D93B4B0"
    "9F708778E41120",
    "previous_txn_lgr_seq": 4,
    "uri": "6469645F6578616D706C65",
    "index": "46813BE38B798B3752CA590D44E7FEADB17485649074403AD1761A2835CE91FF",
}

directory_node_json = {
    "exchange_rate": "4F069BA8FF484000",
    "flags": 0,
    "indexes": ["AD7EAE148287EF12D213A251015F86E6D4BD34B3C4A0A1ED9A17198373F908AD"],
    "ledger_entry_type": "DirectoryNode",
    "root_index": "1BBEF97EDE88D40CEE2ADE6FEF121166AFE80D99EBADB01A4F069BA8FF484000",
    "taker_gets_currency": "0000000000000000000000000000000000000000",
    "taker_gets_issuer": "0000000000000000000000000000000000000000",
    "taker_pays_currency": "0000000000000000000000004A50590000000000",
    "taker_pays_issuer": "5BBC0F22F61D9224A110650CFE21CC0C4BE13098",
    "index": "1BBEF97EDE88D40CEE2ADE6FEF121166AFE80D99EBADB01A4F069BA8FF484000",
}

escrow_json = {
    "account": "rf1BiGeXwwQoi8Z2ueFYTEXSwuJYfV2Jpn",
    "amount": "10000",
    "cancel_after": 545440232,
    "condition": "A0258020A82A88B2DF843A54F58772E4A3861866ECDB4157645DD9AE528C1D3AEEDAB"
    "AB6810120",
    "destination": "ra5nK24KXen9AHvsdFTKHSANinZseWnPcX",
    "destination_tag": 23480,
    "finish_after": 545354132,
    "flags": 0,
    "ledger_entry_type": "Escrow",
    "owner_node": "0000000000000000",
    "destination_node": "0000000000000000",
    "previous_txn_id": "C44F2EB84196B9AD820313DBEBA6316A15C9A2"
    "D35787579ED172B87A30131DA7",
    "previous_txn_lgr_seq": 28991004,
    "source_tag": 11747,
    "index": "DC5F3851D8A1AB622F957761E5963BC5BD439D5C24AC6AD7AC4523F0640244AC",
}

fee_settings_json = {
    "base_fee": "000000000000000A",
    "flags": 0,
    "ledger_entry_type": "FeeSettings",
    "reference_fee_units": 10,
    "reserve_base": 20000000,
    "reserve_increment": 5000000,
    "index": "4BC50C9B0D8515D3EAAE1E74B29A95804346C491EE1A95BF25E4AAB854A6A651",
}

ledger_hashes_json = {
    "ledger_entry_type": "LedgerHashes",
    "flags": 0,
    "first_ledger_sequence": 2,
    "last_ledger_sequence": 33872029,
    "hashes": [
        "D638208ADBD04CBB10DE7B645D3AB4BA31489379411A3A347151702B6401AA78",
        "254D690864E418DDD9BCAC93F41B1F53B1AE693FC5FE667CE40205C322D1BE3B",
        "A2B31D28905E2DEF926362822BC412B12ABF6942B73B72A32D46ED2ABB7ACCFA",
        "AB4014846DF818A4B43D6B1686D0DE0644FE711577C5AB6F0B2A21CCEE280140",
        "3383784E82A8BA45F4DD5EF4EE90A1B2D3B4571317DBAC37B859836ADDE644C1",
    ],
    "index": "B4979A36CDC7F3D3D5C31A4EAE2AC7D7209DDA877588B9AFC66799692AB0D66B",
}

negative_unl_json = {
    "disabled_validators": [
        {
            "disabled_validator": {
                "first_ledger_sequence": 1609728,
                "public_key": "ED6629D456285AE3613B285F65BBFF168D695BA"
                "3921F309949AFCD2CA7AFEC16FE",
            }
        }
    ],
    "flags": 0,
    "ledger_entry_type": "NegativeUNL",
    "index": "2E8A59AA9D3B5B186B0B9E0F62E6C02587CA74A4D778938E957B6357D364B244",
}

nftoken_offer_json = {
    "ledger_entry_type": "NFTokenOffer",
    "index": "AEBABA4FAC212BF28E0F9A9C3788A47B085557EC5D1429E7A8266FB859C863B3",
    "amount": "1000000",
    "flags": 1,
    "nftoken_id": "00081B5825A08C22787716FA031B432EBBC1B101BB54875F0002D2A400000000",
    "owner": "rhRxL3MNvuKEjWjL7TBbZSDacb8PmzAd7m",
    "previous_txn_id": "BFA9BE27383FA315651E26FDE1FA30815C5A5D0544EE10EC33D3E92532993"
    "769",
    "previous_txn_lgr_seq": 75443565,
    "owner_node": "17",
    "nftoken_offer_node": "0",
}

nftoken_page_json = {
    "ledger_entry_type": "NFTokenPage",
    "previous_token_page": "598EDFD7CF73460FB8C695d6a9397E"
    "907378C8A841F7204C793DCBEF5406",
    "previous_token_next": "598EDFD7CF73460FB8C695d6a9397E90"
    "73781BA3B78198904F659AAA252A",
    "previous_txn_id": "95C8761B22894E328646F7A70035E9DFBECC9"
    "0EDD83E43B7B973F626D21A0822",
    "previous_txn_lgr_seq": 42891441,
    "nftokens": [
        {
            "nftoken_id": "000B013A95F14B0044F78A264E41713"
            "C64B5F89242540EE208C3098E00000D65",
            "uri": "697066733A2F2F62616679626569676479727A74357366703775646D3768753736"
            "7568377932366E6634646675796C71616266336F636C67747179353566627A6469",
        },
    ],
    "index": "",
}

offer_json = {
    "account": "rBqb89MRQJnMPq8wTwEbtz4kvxrEDfcYvt",
    "book_directory": "ACC27DE91DBA86FC509069EAF4BC511D7"
    "3128B780F2E54BF5E07A369E2446000",
    "book_node": "0000000000000000",
    "flags": 131072,
    "ledger_entry_type": "Offer",
    "owner_node": "0000000000000000",
    "previous_txn_id": "F0AB71E777B2DA54B86231E19B82554EF1"
    "F8211F92ECA473121C655BFC5329BF",
    "previous_txn_lgr_seq": 14524914,
    "sequence": 866,
    "taker_gets": {
        "currency": "XAG",
        "issuer": "r9Dr5xwkeLegBeXq6ujinjSBLQzQ1zQGjH",
        "value": "37",
    },
    "taker_pays": "79550000000",
    "index": "96F76F27D8A327FC48753167EC04A46AA0E382E6F57F32FD12274144D00F1797",
}

pay_channel_json = {
    "account": "rBqb89MRQJnMPq8wTwEbtz4kvxrEDfcYvt",
    "destination": "rf1BiGeXwwQoi8Z2ueFYTEXSwuJYfV2Jpn",
    "amount": "4325800",
    "balance": "2323423",
    "public_key": "32D2471DB72B27E3310F355BB33E339BF26F8392D5A93D3BC0FC3B566612DA0F0A",
    "settle_delay": 3600,
    "expiration": 536027313,
    "cancel_after": 536891313,
    "source_tag": 0,
    "destination_tag": 1002341,
    "destination_node": "0000000000000000",
    "flags": 0,
    "ledger_entry_type": "PayChannel",
    "owner_node": "0000000000000000",
    "previous_txn_id": "F0AB71E777B2DA54B86231E19B82554E"
    "F1F8211F92ECA473121C655BFC5329BF",
    "previous_txn_lgr_seq": 14524914,
    "index": "96F76F27D8A327FC48753167EC04A46AA0E382E6F57F32FD12274144D00F1797",
}

ripple_state_json = {
    "balance": {
        "currency": "USD",
        "issuer": "rrrrrrrrrrrrrrrrrrrrBZbvji",
        "value": "-10",
    },
    "flags": 393216,
    "high_limit": {
        "currency": "USD",
        "issuer": "rf1BiGeXwwQoi8Z2ueFYTEXSwuJYfV2Jpn",
        "value": "110",
    },
    "high_node": "0000000000000000",
    "ledger_entry_type": "RippleState",
    "low_limit": {
        "currency": "USD",
        "issuer": "rsA2LpzuawewSBQXkiju3YQTMzW13pAAdW",
        "value": "0",
    },
    "low_node": "0000000000000000",
    "previous_txn_id": "E3FE6EA3D48F0C2B639448020EA4F03D"
    "4F4F8FFDB243A852A0F59177921B4879",
    "previous_txn_lgr_seq": 14090896,
    "index": "9CA88CDEDFF9252B3DE183CE35B038F57282BC9503CDFA1923EF9A95DF0D6F7B",
}

signer_list_json = {
    "flags": 0,
    "ledger_entry_type": "SignerList",
    "owner_node": "0000000000000000",
    "previous_txn_id": "5904C0DC72C58A83AEFED2FFC5386356"
    "AA83FCA6A88C89D00646E51E687CDBE4",
    "previous_txn_lgr_seq": 16061435,
    "signer_entries": [
        {
            "signer_entry": {
                "account": "rsA2LpzuawewSBQXkiju3YQTMzW13pAAdW",
                "signer_weight": 2,
            }
        },
        {
            "signer_entry": {
                "account": "raKEEVSGnKSD9Zyvxu4z6Pqpm4ABH8FS6n",
                "signer_weight": 1,
            }
        },
        {
            "signer_entry": {
                "account": "rUpy3eEg8rqjqfUoLeBnZkscbKbFsKXC3v",
                "signer_weight": 1,
            }
        },
    ],
    "signer_list_id": 0,
    "signer_quorum": 3,
    "index": "A9C28A28B85CD533217F5C0A0C7767666B093FA58A0F2D80026FCC4CD932DDC7",
}

ticket_json = {
    "account": "rEhxGqkqPPSxQ3P25J66ft5TwpzV14k2de",
    "flags": 0,
    "ledger_entry_type": "Ticket",
    "owner_node": "0000000000000000",
    "previous_txn_id": "F19AD4577212D3BEACA0F75FE1BA1"
    "644F2E854D46E8D62E9C95D18E9708CBFB1",
    "previous_txn_lgr_seq": 4,
    "ticket_sequence": 3,
    "index": "",  # TODO: Find out if there is an unique index
}


class TestFromTODict(TestCase):
    def test_account_root(self):
        actual = AccountRoot.from_dict(account_root_json)
        expected = AccountRoot(
            index="13F1A95D7AAB7108D5CE7EEAF504B2894B8C674E6D68499076441C4837282BF8",
            account="rf1BiGeXwwQoi8Z2ueFYTEXSwuJYfV2Jpn",
            balance="148446663",
            flags=8388608,
            owner_count=3,
            previous_txn_id="0D5FB50FA65C9FE1538FD7E398FFFE9D"
            "1908DFA4576D8D7A020040686F93C77D",
            previous_txn_lgr_seq=14091160,
            sequence=336,
            account_txn_id="0D5FB50FA65C9FE1538FD7E398FFFE9D1"
            "908DFA4576D8D7A020040686F93C77D",
            burned_nftokens=None,
            domain="6D64756F31332E636F6D",
            email_hash="98B4375E1D753E5B91627516F6D70977",
            message_key="0000000000000000000000070000000300",
            minted_nftokens=None,
            nftoken_minter="rHello",
            regular_key=None,
            ticket_count=None,
            ticket_size=None,
            transfer_rate=1004999999,
            wallet_locator=None,
            wallet_size=None,
        )
        self.assertEqual(actual, expected)
        self.assertEqual(account_root_json, expected.to_dict())

    def test_amendments(self):
        actual = Amendments.from_dict(amendment_json)
        expected = Amendments(
            index="7DB0788C020F02780A673DC74757F23823FA3014C1866E72CC4CD8B226CD6EF4",
            flags=0,
            amendments=[
                "42426C4D4F1009EE67080A9B7965B44656D7714D104A72F9B4369F97ABF044EE",
                "4C97EBA926031A7CF7D7B36FDE3ED66DDA5421192D63DE53FFB46E43B9DC8373",
                "6781F8368C4771B83E8B821D88F580202BCB4228075297B19E4FDC5233F1EFDC",
                "740352F2412A9909880C23A559FCECEDA3BE2126FED62FC7660D628A06927F11",
            ],
            majorities=[
                Majority(
                    amendment="1562511F573A19AE9BD103B5D6B9E01B3B46805AEC5D3C"
                    "4805C902B514399146",
                    close_time=535589001,
                )
            ],
        )
        self.assertEqual(actual, expected)
        self.assertEqual(amendment_json, expected.to_dict())

    def test_amm(self):
        actual = AMM.from_dict(amm_json)
        expected = AMM(
            account="rE54zDvgnghAoPopCgvtiqWNq3dU5y836S",
            asset=XRP(),
            asset2=IssuedCurrency(
                currency="TST",
                issuer="rP9jPyP5kyvFRb6ZiRghAGw5u8SGAmU4bd",
            ),
            auction_slot=AuctionSlot(
                account="rJVUeRqDFNs2xqA7ncVE6ZoAhPUoaJJSQm",
                auth_accounts=[
                    AuthAccount(account="rMKXGCbJ5d8LbrqthdG46q3f969MVK2Qeg"),
                    AuthAccount(account="rBepJuTLFJt3WmtLXYAxSjtBWAeQxVbncv"),
                ],
                discounted_fee=0,
                expiration=721870180,
                price=IssuedCurrencyAmount(
                    currency="039C99CD9AB0B70B32ECDA51EAAE471625608EA2",
                    issuer="rE54zDvgnghAoPopCgvtiqWNq3dU5y836S",
                    value="0.8696263565463045",
                ),
            ),
            flags=0,
            lptoken_balance=IssuedCurrencyAmount(
                currency="039C99CD9AB0B70B32ECDA51EAAE471625608EA2",
                issuer="rE54zDvgnghAoPopCgvtiqWNq3dU5y836S",
                value="71150.53584131501",
            ),
            trading_fee=600,
            vote_slots=[
                VoteEntry(
                    account="rJVUeRqDFNs2xqA7ncVE6ZoAhPUoaJJSQm",
                    trading_fee=600,
                    vote_weight=100000,
                ),
            ],
        )
        self.assertEqual(actual, expected)
        self.assertEqual(amm_json, expected.to_dict())

    def test_bridge(self):
        actual = Bridge.from_dict(bridge_json)
        expected = Bridge(
            account="r3nCVTbZGGYoWvZ58BcxDmiMUU7ChMa1eC",
            flags=0,
            min_account_create_amount="2000000000",
            owner_node="0",
            previous_txn_id="67A8A1B36C1B97BE3AAB6B19CB3A3069034877DE917FD1A71919EAE75"
            "48E5636",
            previous_txn_lgr_seq=102,
            signature_reward="204",
            xchain_account_claim_count="0",
            xchain_account_create_count="0",
            xchain_bridge=XChainBridge(
                issuing_chain_door="rHb9CJAWyB4rj91VRWn96DkukG4bwdtyTh",
                issuing_chain_issue=XRP(),
                locking_chain_door="r3nCVTbZGGYoWvZ58BcxDmiMUU7ChMa1eC",
                locking_chain_issue=XRP(),
            ),
            xchain_claim_id="1",
            index="9F2C9E23343852036AFD323025A8506018ABF9D4DBAA746D61BF1CFB5C297D10",
        )
        self.assertEqual(actual, expected)
        self.assertEqual(bridge_json, expected.to_dict())

    def test_check(self):
        actual = Check.from_dict(check_json)
        expected = Check(
            index="49647F0D748DC3FE26BDACBC57F251AADEFFF391403EC9BF87C97F67E9977FB0",
            account="rUn84CUYbNjRoTQ6mSW7BVJPSVJNLb1QLo",
            destination="rfkE1aSy9G8Upk4JssnwBxhEv5p4mn2KTy",
            flags=0,
            owner_node="0000000000000000",
            previous_txn_id="5463C6E08862A1FAE5EDAC12D70ADB16546A"
            "1F674930521295BC082494B62924",
            previous_txn_lgr_seq=6,
            send_max="100000000",
            sequence=2,
            destination_node="0000000000000000",
            destination_tag=1,
            expiration=570113521,
            invoice_id="46060241FABCF692D4D934BA2A6C4427CD427"
            "9083E38C77CBE642243E43BE291",
            source_tag=None,
        )
        self.assertEqual(actual, expected)
        self.assertEqual(check_json, expected.to_dict())

    def test_deposit_preauth(self):
        actual = DepositPreauth.from_dict(deposit_preauth_json)
        expected = DepositPreauth(
            index="4A255038CC3ADCC1A9C91509279B59908251728D0DAADB248FFE297D0F7E068C",
            account="rsUiUMpnrgxQp24dJYZDhmV4bE3aBtQyt8",
            authorize="rEhxGqkqPPSxQ3P25J66ft5TwpzV14k2de",
            flags=0,
            owner_node="0000000000000000",
            previous_txn_id="3E8964D5A86B3CD6B9ECB33310D4E073D64C8"
            "65A5B866200AD2B7E29F8326702",
            previous_txn_lgr_seq=7,
        )
        self.assertEqual(actual, expected)
        self.assertEqual(deposit_preauth_json, expected.to_dict())

    def test_did(self):
        actual = DID.from_dict(did_json)
        expected = DID(
            account="rpfqJrXg5uidNo2ZsRhRY6TiF1cvYmV9Fg",
            did_document="646F63",
            data="617474657374",
            flags=0,
            owner_node="0",
            previous_txn_id="A4C15DA185E6092DF5954FF62A1446220C61A5F60F0D93B4B09F"
            "708778E41120",
            previous_txn_lgr_seq=4,
            uri="6469645F6578616D706C65",
            index="46813BE38B798B3752CA590D44E7FEADB17485649074403AD1761A2835CE91FF",
        )
        self.assertEqual(actual, expected)
        self.assertEqual(did_json, expected.to_dict())

    def test_directory_node(self):
        actual = DirectoryNode.from_dict(directory_node_json)
        expected = DirectoryNode(
            index="1BBEF97EDE88D40CEE2ADE6FEF121166AFE80D99EBADB01A4F069BA8FF484000",
            flags=0,
            root_index="1BBEF97EDE88D40CEE2ADE6FEF121166A"
            "FE80D99EBADB01A4F069BA8FF484000",
            indexes=[
                "AD7EAE148287EF12D213A251015F86E6D4BD34B3C4A0A1ED9A17198373F908AD"
            ],
            index_next=None,
            index_previous=None,
            owner=None,
            exchange_rate="4F069BA8FF484000",
            taker_pays_currency="0000000000000000000000004A50590000000000",
            taker_pays_issuer="5BBC0F22F61D9224A110650CFE21CC0C4BE13098",
            taker_gets_currency="0000000000000000000000000000000000000000",
            taker_gets_issuer="0000000000000000000000000000000000000000",
        )
        self.assertEqual(actual, expected)
        self.assertEqual(directory_node_json, expected.to_dict())

    def test_escrow(self):
        actual = Escrow.from_dict(escrow_json)
        expected = Escrow(
            index="DC5F3851D8A1AB622F957761E5963BC5BD439D5C24AC6AD7AC4523F0640244AC",
            account="rf1BiGeXwwQoi8Z2ueFYTEXSwuJYfV2Jpn",
            amount="10000",
            destination="ra5nK24KXen9AHvsdFTKHSANinZseWnPcX",
            flags=0,
            owner_node="0000000000000000",
            previous_txn_id="C44F2EB84196B9AD820313DBEBA6316A15"
            "C9A2D35787579ED172B87A30131DA7",
            previous_txn_lgr_seq=28991004,
            condition="A0258020A82A88B2DF843A54F58772E4A3861866EC"
            "DB4157645DD9AE528C1D3AEEDABAB6810120",
            cancel_after=545440232,
            destination_node="0000000000000000",
            destination_tag=23480,
            finish_after=545354132,
            source_tag=11747,
        )
        self.assertEqual(actual, expected)
        self.assertEqual(escrow_json, expected.to_dict())

    def test_fee_settings(self):
        actual = FeeSettings.from_dict(fee_settings_json)
        expected = FeeSettings(
            index="4BC50C9B0D8515D3EAAE1E74B29A95804346C491EE1A95BF25E4AAB854A6A651",
            base_fee="000000000000000A",
            flags=0,
            reference_fee_units=10,
            reserve_base=20000000,
            reserve_increment=5000000,
        )
        self.assertEqual(actual, expected)
        self.assertEqual(fee_settings_json, expected.to_dict())

    def test_ledger_hashes(self):
        actual = LedgerHashes.from_dict(ledger_hashes_json)
        expected = LedgerHashes(
            index="B4979A36CDC7F3D3D5C31A4EAE2AC7D7209DDA877588B9AFC66799692AB0D66B",
            first_ledger_sequence=2,
            last_ledger_sequence=33872029,
            hashes=[
                "D638208ADBD04CBB10DE7B645D3AB4BA31489379411A3A347151702B6401AA78",
                "254D690864E418DDD9BCAC93F41B1F53B1AE693FC5FE667CE40205C322D1BE3B",
                "A2B31D28905E2DEF926362822BC412B12ABF6942B73B72A32D46ED2ABB7ACCFA",
                "AB4014846DF818A4B43D6B1686D0DE0644FE711577C5AB6F0B2A21CCEE280140",
                "3383784E82A8BA45F4DD5EF4EE90A1B2D3B4571317DBAC37B859836ADDE644C1",
            ],
            flags=0,
        )
        self.assertEqual(actual, expected)
        self.assertEqual(ledger_hashes_json, expected.to_dict())

    def test_negative_unl(self):
        actual = NegativeUNL.from_dict(negative_unl_json)
        expected = NegativeUNL(
            index="2E8A59AA9D3B5B186B0B9E0F62E6C02587CA74A4D778938E957B6357D364B244",
            flags=0,
            disabled_validators=[
                DisabledValidator(
                    first_ledger_sequence=1609728,
                    public_key="ED6629D456285AE3613B285F65BBFF168D695BA"
                    "3921F309949AFCD2CA7AFEC16FE",
                )
            ],
            validator_to_disable=None,
            validator_to_enable=None,
        )
        self.assertEqual(actual, expected)
        self.assertEqual(negative_unl_json, expected.to_dict())

    def test_nftoken_offer(self):
        actual = NFTokenOffer.from_dict(nftoken_offer_json)
        expected = NFTokenOffer(
            index="AEBABA4FAC212BF28E0F9A9C3788A47B085557EC5D1429E7A8266FB859C863B3",
            amount="1000000",
            flags=1,
            nftoken_id="00081B5825A08C22787716FA031B432EBBC1B101BB54875F0002D2A400000"
            "000",
            owner="rhRxL3MNvuKEjWjL7TBbZSDacb8PmzAd7m",
            previous_txn_id="BFA9BE27383FA315651E26FDE1FA30815C5A5D0544EE10EC33D3E925"
            "32993769",
            previous_txn_lgr_seq=75443565,
            owner_node="17",
            nftoken_offer_node="0",
        )
        self.assertEqual(actual, expected)
        self.assertEqual(nftoken_offer_json, expected.to_dict())

    def test_nftoken_page(self):
        actual = NFTokenPage.from_dict(nftoken_page_json)
        expected = NFTokenPage(
            index="",
            previous_page_min=None,
            next_page_min=None,
            previous_token_page="598EDFD7CF73460FB8C695d6a9397E9"
            "07378C8A841F7204C793DCBEF5406",
            previous_token_next="598EDFD7CF73460FB8C695d6a9397E90"
            "73781BA3B78198904F659AAA252A",
            previous_txn_id="95C8761B22894E328646F7A70035E9DFBEC"
            "C90EDD83E43B7B973F626D21A0822",
            previous_txn_lgr_seq=42891441,
            nftokens=[
                NFToken(
                    nftoken_id="000B013A95F14B0044F78A264E41713"
                    "C64B5F89242540EE208C3098E00000D65",
                    uri="697066733A2F2F62616679626569676479727A"
                    "74357366703775646D37687537367568377932366E"
                    "6634646675796C71616266336F636C67747179353566627A6469",
                )
            ],
        )
        self.assertEqual(actual, expected)
        self.assertEqual(nftoken_page_json, expected.to_dict())

    def test_offer(self):
        actual = Offer.from_dict(offer_json)
        expected = Offer(
            index="96F76F27D8A327FC48753167EC04A46AA0E382E6F57F32FD12274144D00F1797",
            account="rBqb89MRQJnMPq8wTwEbtz4kvxrEDfcYvt",
            taker_gets=IssuedCurrencyAmount(
                currency="XAG", issuer="r9Dr5xwkeLegBeXq6ujinjSBLQzQ1zQGjH", value="37"
            ),
            taker_pays="79550000000",
            sequence=866,
            flags=131072,
            book_directory="ACC27DE91DBA86FC509069EAF4BC511D7"
            "3128B780F2E54BF5E07A369E2446000",
            book_node="0000000000000000",
            owner_node="0000000000000000",
            previous_txn_id="F0AB71E777B2DA54B86231E19B82554EF1F821"
            "1F92ECA473121C655BFC5329BF",
            previous_txn_lgr_seq=14524914,
            expiration=None,
        )
        self.assertEqual(actual, expected)
        self.assertEqual(offer_json, expected.to_dict())

    def test_pay_channel(self):
        actual = PayChannel.from_dict(pay_channel_json)
        expected = PayChannel(
            index="96F76F27D8A327FC48753167EC04A46AA0E382E6F57F32FD12274144D00F1797",
            account="rBqb89MRQJnMPq8wTwEbtz4kvxrEDfcYvt",
            amount="4325800",
            balance="2323423",
            destination="rf1BiGeXwwQoi8Z2ueFYTEXSwuJYfV2Jpn",
            flags=0,
            owner_node="0000000000000000",
            public_key="32D2471DB72B27E3310F355BB33E339BF26F83"
            "92D5A93D3BC0FC3B566612DA0F0A",
            previous_txn_id="F0AB71E777B2DA54B86231E19B82554EF1"
            "F8211F92ECA473121C655BFC5329BF",
            previous_txn_lgr_seq=14524914,
            settle_delay=3600,
            destination_node="0000000000000000",
            destination_tag=1002341,
            expiration=536027313,
            cancel_after=536891313,
            source_tag=0,
        )
        self.assertEqual(actual, expected)
        self.assertEqual(pay_channel_json, expected.to_dict())

    def test_ripple_state(self):
        actual = RippleState.from_dict(ripple_state_json)
        expected = RippleState(
            index="9CA88CDEDFF9252B3DE183CE35B038F57282BC9503CDFA1923EF9A95DF0D6F7B",
            balance=IssuedCurrencyAmount(
                currency="USD", issuer="rrrrrrrrrrrrrrrrrrrrBZbvji", value="-10"
            ),
            flags=393216,
            low_limit=IssuedCurrencyAmount(
                currency="USD", issuer="rsA2LpzuawewSBQXkiju3YQTMzW13pAAdW", value="0"
            ),
            high_limit=IssuedCurrencyAmount(
                currency="USD", issuer="rf1BiGeXwwQoi8Z2ueFYTEXSwuJYfV2Jpn", value="110"
            ),
            previous_txn_id="E3FE6EA3D48F0C2B639448020EA4F03D4F4"
            "F8FFDB243A852A0F59177921B4879",
            previous_txn_lgr_seq=14090896,
            high_node="0000000000000000",
            low_node="0000000000000000",
            high_quality_in=None,
            high_quality_out=None,
            low_quality_in=None,
            low_quality_out=None,
        )
        self.assertEqual(actual, expected)
        self.assertEqual(ripple_state_json, expected.to_dict())

    def test_signer_list(self):
        actual = SignerList.from_dict(signer_list_json)
        expected = SignerList(
            index="A9C28A28B85CD533217F5C0A0C7767666B093FA58A0F2D80026FCC4CD932DDC7",
            flags=0,
            owner_node="0000000000000000",
            previous_txn_id="5904C0DC72C58A83AEFED2FFC5386356"
            "AA83FCA6A88C89D00646E51E687CDBE4",
            previous_txn_lgr_seq=16061435,
            signer_entries=[
                SignerEntry(
                    account="rsA2LpzuawewSBQXkiju3YQTMzW13pAAdW",
                    signer_weight=2,
                ),
                SignerEntry(
                    account="raKEEVSGnKSD9Zyvxu4z6Pqpm4ABH8FS6n",
                    signer_weight=1,
                ),
                SignerEntry(
                    account="rUpy3eEg8rqjqfUoLeBnZkscbKbFsKXC3v",
                    signer_weight=1,
                ),
            ],
            signer_list_id=0,
            signer_quorum=3,
        )
        self.assertEqual(actual, expected)
        self.assertEqual(signer_list_json, expected.to_dict())

    def test_ticket(self):
        actual = Ticket.from_dict(ticket_json)
        expected = Ticket(
            index="",
            account="rEhxGqkqPPSxQ3P25J66ft5TwpzV14k2de",
            flags=0,
            owner_node="0000000000000000",
            previous_txn_id="F19AD4577212D3BEACA0F75FE1BA1644F2E85"
            "4D46E8D62E9C95D18E9708CBFB1",
            previous_txn_lgr_seq=4,
            ticket_sequence=3,
        )
        self.assertEqual(actual, expected)
        self.assertEqual(ticket_json, expected.to_dict())
