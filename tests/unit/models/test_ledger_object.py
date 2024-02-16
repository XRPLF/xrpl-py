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
from xrpl.models.ledger_objects.ledger_object import LedgerObject
from xrpl.models.ledger_objects.xchain_owned_claim_id import (
    XChainClaimProofSig,
    XChainOwnedClaimID,
)
from xrpl.models.ledger_objects.xchain_owned_create_account_claim_id import (
    XChainCreateAccountProofSig,
    XChainOwnedCreateAccountClaimID,
)
from xrpl.models.xchain_bridge import XChainBridge

account_root_json = {
    "Account": "rf1BiGeXwwQoi8Z2ueFYTEXSwuJYfV2Jpn",
    "AccountTxnID": "0D5FB50FA65C9FE1538FD7E398FFFE9D190"
    "8DFA4576D8D7A020040686F93C77D",
    "Balance": "148446663",
    "Domain": "6D64756F31332E636F6D",
    "EmailHash": "98B4375E1D753E5B91627516F6D70977",
    "Flags": 8388608,
    "LedgerEntryType": "AccountRoot",
    "MessageKey": "0000000000000000000000070000000300",
    "OwnerCount": 3,
    "NFTokenMinter": "rHello",
    "PreviousTxnID": "0D5FB50FA65C9FE1538FD7E398FFFE9D1908DFA4576D8D7A0200"
    "40686F93C77D",
    "PreviousTxnLgrSeq": 14091160,
    "Sequence": 336,
    "TransferRate": 1004999999,
    "index": "13F1A95D7AAB7108D5CE7EEAF504B2894B8C674E6D68499076441C4837282BF8",
}

amendment_json = {
    "Majorities": [
        {
            "Majority": {
                "Amendment": "1562511F573A19AE9BD103B5D6B9E01B3B46805AEC5D3C4805C902B51"
                "4399146",
                "CloseTime": 535589001,
            }
        }
    ],
    "Amendments": [
        "42426C4D4F1009EE67080A9B7965B44656D7714D104A72F9B4369F97ABF044EE",
        "4C97EBA926031A7CF7D7B36FDE3ED66DDA5421192D63DE53FFB46E43B9DC8373",
        "6781F8368C4771B83E8B821D88F580202BCB4228075297B19E4FDC5233F1EFDC",
        "740352F2412A9909880C23A559FCECEDA3BE2126FED62FC7660D628A06927F11",
    ],
    "Flags": 0,
    "LedgerEntryType": "Amendments",
    "index": "7DB0788C020F02780A673DC74757F23823FA3014C1866E72CC4CD8B226CD6EF4",
}

amm_json = {
    "Account": "rE54zDvgnghAoPopCgvtiqWNq3dU5y836S",
    "Asset": {"currency": "XRP"},
    "Asset2": {"currency": "TST", "issuer": "rP9jPyP5kyvFRb6ZiRghAGw5u8SGAmU4bd"},
    "AuctionSlot": {
        "Account": "rJVUeRqDFNs2xqA7ncVE6ZoAhPUoaJJSQm",
        "AuthAccounts": [
            {"AuthAccount": {"Account": "rMKXGCbJ5d8LbrqthdG46q3f969MVK2Qeg"}},
            {"AuthAccount": {"Account": "rBepJuTLFJt3WmtLXYAxSjtBWAeQxVbncv"}},
        ],
        "DiscountedFee": 0,
        "Expiration": 721870180,
        "Price": {
            "currency": "039C99CD9AB0B70B32ECDA51EAAE471625608EA2",
            "issuer": "rE54zDvgnghAoPopCgvtiqWNq3dU5y836S",
            "value": "0.8696263565463045",
        },
    },
    "LPTokenBalance": {
        "currency": "039C99CD9AB0B70B32ECDA51EAAE471625608EA2",
        "issuer": "rE54zDvgnghAoPopCgvtiqWNq3dU5y836S",
        "value": "71150.53584131501",
    },
    "TradingFee": 600,
    "VoteSlots": [
        {
            "VoteEntry": {
                "Account": "rJVUeRqDFNs2xqA7ncVE6ZoAhPUoaJJSQm",
                "TradingFee": 600,
                "VoteWeight": 100000,
            }
        }
    ],
    "OwnerNode": "0",
    "Flags": 0,
    "LedgerEntryType": "AMM",
}

bridge_json = {
    "Account": "r3nCVTbZGGYoWvZ58BcxDmiMUU7ChMa1eC",
    "Flags": 0,
    "LedgerEntryType": "Bridge",
    "MinAccountCreateAmount": "2000000000",
    "OwnerNode": "0",
    "PreviousTxnID": "67A8A1B36C1B97BE3AAB6B19CB3A3069034877DE917FD1A71919EAE7548E56"
    "36",
    "PreviousTxnLgrSeq": 102,
    "SignatureReward": "204",
    "XChainAccountClaimCount": "0",
    "XChainAccountCreateCount": "0",
    "XChainBridge": {
        "IssuingChainDoor": "rHb9CJAWyB4rj91VRWn96DkukG4bwdtyTh",
        "IssuingChainIssue": {"currency": "XRP"},
        "LockingChainDoor": "r3nCVTbZGGYoWvZ58BcxDmiMUU7ChMa1eC",
        "LockingChainIssue": {"currency": "XRP"},
    },
    "XChainClaimID": "1",
    "index": "9F2C9E23343852036AFD323025A8506018ABF9D4DBAA746D61BF1CFB5C297D10",
}

check_json = {
    "Account": "rUn84CUYbNjRoTQ6mSW7BVJPSVJNLb1QLo",
    "Destination": "rfkE1aSy9G8Upk4JssnwBxhEv5p4mn2KTy",
    "DestinationNode": "0000000000000000",
    "DestinationTag": 1,
    "Expiration": 570113521,
    "Flags": 0,
    "InvoiceID": "46060241FABCF692D4D934BA2A6C4427CD4279083E38C77CBE642243E43BE291",
    "LedgerEntryType": "Check",
    "OwnerNode": "0000000000000000",
    "PreviousTxnID": "5463C6E08862A1FAE5EDAC12D70ADB16546A1F67"
    "4930521295BC082494B62924",
    "PreviousTxnLgrSeq": 6,
    "SendMax": "100000000",
    "Sequence": 2,
    "index": "49647F0D748DC3FE26BDACBC57F251AADEFFF391403EC9BF87C97F67E9977FB0",
}

deposit_preauth_json = {
    "LedgerEntryType": "DepositPreauth",
    "Account": "rsUiUMpnrgxQp24dJYZDhmV4bE3aBtQyt8",
    "Authorize": "rEhxGqkqPPSxQ3P25J66ft5TwpzV14k2de",
    "Flags": 0,
    "OwnerNode": "0000000000000000",
    "PreviousTxnID": "3E8964D5A86B3CD6B9ECB33310D4E073D64C865A5B866200"
    "AD2B7E29F8326702",
    "PreviousTxnLgrSeq": 7,
    "index": "4A255038CC3ADCC1A9C91509279B59908251728D0DAADB248FFE297D0F7E068C",
}

did_json = {
    "Account": "rpfqJrXg5uidNo2ZsRhRY6TiF1cvYmV9Fg",
    "DIDDocument": "646F63",
    "Data": "617474657374",
    "Flags": 0,
    "LedgerEntryType": "DID",
    "OwnerNode": "0",
    "PreviousTxnID": "A4C15DA185E6092DF5954FF62A1446220C61A5F60F0D93B4B0"
    "9F708778E41120",
    "PreviousTxnLgrSeq": 4,
    "URI": "6469645F6578616D706C65",
    "index": "46813BE38B798B3752CA590D44E7FEADB17485649074403AD1761A2835CE91FF",
}

directory_node_json = {
    "ExchangeRate": "4F069BA8FF484000",
    "Flags": 0,
    "Indexes": ["AD7EAE148287EF12D213A251015F86E6D4BD34B3C4A0A1ED9A17198373F908AD"],
    "LedgerEntryType": "DirectoryNode",
    "RootIndex": "1BBEF97EDE88D40CEE2ADE6FEF121166AFE80D99EBADB01A4F069BA8FF484000",
    "TakerGetsCurrency": "0000000000000000000000000000000000000000",
    "TakerGetsIssuer": "0000000000000000000000000000000000000000",
    "TakerPaysCurrency": "0000000000000000000000004A50590000000000",
    "TakerPaysIssuer": "5BBC0F22F61D9224A110650CFE21CC0C4BE13098",
    "index": "1BBEF97EDE88D40CEE2ADE6FEF121166AFE80D99EBADB01A4F069BA8FF484000",
}

escrow_json = {
    "Account": "rf1BiGeXwwQoi8Z2ueFYTEXSwuJYfV2Jpn",
    "Amount": "10000",
    "CancelAfter": 545440232,
    "Condition": "A0258020A82A88B2DF843A54F58772E4A3861866ECDB4157645DD9AE528C1D3AEEDAB"
    "AB6810120",
    "Destination": "ra5nK24KXen9AHvsdFTKHSANinZseWnPcX",
    "DestinationTag": 23480,
    "FinishAfter": 545354132,
    "Flags": 0,
    "LedgerEntryType": "Escrow",
    "OwnerNode": "0000000000000000",
    "DestinationNode": "0000000000000000",
    "PreviousTxnID": "C44F2EB84196B9AD820313DBEBA6316A15C9A2"
    "D35787579ED172B87A30131DA7",
    "PreviousTxnLgrSeq": 28991004,
    "SourceTag": 11747,
    "index": "DC5F3851D8A1AB622F957761E5963BC5BD439D5C24AC6AD7AC4523F0640244AC",
}

fee_settings_json = {
    "BaseFee": "000000000000000A",
    "Flags": 0,
    "LedgerEntryType": "FeeSettings",
    "ReferenceFeeUnits": 10,
    "ReserveBase": 20000000,
    "ReserveIncrement": 5000000,
    "index": "4BC50C9B0D8515D3EAAE1E74B29A95804346C491EE1A95BF25E4AAB854A6A651",
}

ledger_hashes_json = {
    "LedgerEntryType": "LedgerHashes",
    "Flags": 0,
    "FirstLedgerSequence": 2,
    "LastLedgerSequence": 33872029,
    "Hashes": [
        "D638208ADBD04CBB10DE7B645D3AB4BA31489379411A3A347151702B6401AA78",
        "254D690864E418DDD9BCAC93F41B1F53B1AE693FC5FE667CE40205C322D1BE3B",
        "A2B31D28905E2DEF926362822BC412B12ABF6942B73B72A32D46ED2ABB7ACCFA",
        "AB4014846DF818A4B43D6B1686D0DE0644FE711577C5AB6F0B2A21CCEE280140",
        "3383784E82A8BA45F4DD5EF4EE90A1B2D3B4571317DBAC37B859836ADDE644C1",
    ],
    "index": "B4979A36CDC7F3D3D5C31A4EAE2AC7D7209DDA877588B9AFC66799692AB0D66B",
}

negative_unl_json = {
    "DisabledValidators": [
        {
            "DisabledValidator": {
                "FirstLedgerSequence": 1609728,
                "PublicKey": "ED6629D456285AE3613B285F65BBFF168D695BA"
                "3921F309949AFCD2CA7AFEC16FE",
            }
        }
    ],
    "Flags": 0,
    "LedgerEntryType": "NegativeUNL",
    "index": "2E8A59AA9D3B5B186B0B9E0F62E6C02587CA74A4D778938E957B6357D364B244",
}

nftoken_offer_json = {
    "LedgerEntryType": "NFTokenOffer",
    "index": "AEBABA4FAC212BF28E0F9A9C3788A47B085557EC5D1429E7A8266FB859C863B3",
    "Amount": "1000000",
    "Flags": 1,
    "NFTokenID": "00081B5825A08C22787716FA031B432EBBC1B101BB54875F0002D2A400000000",
    "Owner": "rhRxL3MNvuKEjWjL7TBbZSDacb8PmzAd7m",
    "PreviousTxnID": "BFA9BE27383FA315651E26FDE1FA30815C5A5D0544EE10EC33D3E92532993"
    "769",
    "PreviousTxnLgrSeq": 75443565,
    "OwnerNode": "17",
    "NFTokenOfferNode": "0",
}

nftoken_page_json = {
    "Flags": 0,
    "LedgerEntryType": "NFTokenPage",
    "PreviousTxnID": "95C8761B22894E328646F7A70035E9DFBECC9"
    "0EDD83E43B7B973F626D21A0822",
    "PreviousTxnLgrSeq": 42891441,
    "NFTokens": [
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
    "Account": "rBqb89MRQJnMPq8wTwEbtz4kvxrEDfcYvt",
    "BookDirectory": "ACC27DE91DBA86FC509069EAF4BC511D7"
    "3128B780F2E54BF5E07A369E2446000",
    "BookNode": "0000000000000000",
    "Flags": 131072,
    "LedgerEntryType": "Offer",
    "OwnerNode": "0000000000000000",
    "PreviousTxnID": "F0AB71E777B2DA54B86231E19B82554EF1"
    "F8211F92ECA473121C655BFC5329BF",
    "PreviousTxnLgrSeq": 14524914,
    "Sequence": 866,
    "TakerGets": {
        "currency": "XAG",
        "issuer": "r9Dr5xwkeLegBeXq6ujinjSBLQzQ1zQGjH",
        "value": "37",
    },
    "TakerPays": "79550000000",
    "index": "96F76F27D8A327FC48753167EC04A46AA0E382E6F57F32FD12274144D00F1797",
}

pay_channel_json = {
    "Account": "rBqb89MRQJnMPq8wTwEbtz4kvxrEDfcYvt",
    "Destination": "rf1BiGeXwwQoi8Z2ueFYTEXSwuJYfV2Jpn",
    "Amount": "4325800",
    "Balance": "2323423",
    "PublicKey": "32D2471DB72B27E3310F355BB33E339BF26F8392D5A93D3BC0FC3B566612DA0F0A",
    "SettleDelay": 3600,
    "Expiration": 536027313,
    "CancelAfter": 536891313,
    "SourceTag": 0,
    "DestinationTag": 1002341,
    "DestinationNode": "0000000000000000",
    "Flags": 0,
    "LedgerEntryType": "PayChannel",
    "OwnerNode": "0000000000000000",
    "PreviousTxnID": "F0AB71E777B2DA54B86231E19B82554E"
    "F1F8211F92ECA473121C655BFC5329BF",
    "PreviousTxnLgrSeq": 14524914,
    "index": "96F76F27D8A327FC48753167EC04A46AA0E382E6F57F32FD12274144D00F1797",
}

ripple_state_json = {
    "Balance": {
        "currency": "USD",
        "issuer": "rrrrrrrrrrrrrrrrrrrrBZbvji",
        "value": "-10",
    },
    "Flags": 393216,
    "HighLimit": {
        "currency": "USD",
        "issuer": "rf1BiGeXwwQoi8Z2ueFYTEXSwuJYfV2Jpn",
        "value": "110",
    },
    "HighNode": "0000000000000000",
    "LedgerEntryType": "RippleState",
    "LowLimit": {
        "currency": "USD",
        "issuer": "rsA2LpzuawewSBQXkiju3YQTMzW13pAAdW",
        "value": "0",
    },
    "LowNode": "0000000000000000",
    "PreviousTxnID": "E3FE6EA3D48F0C2B639448020EA4F03D"
    "4F4F8FFDB243A852A0F59177921B4879",
    "PreviousTxnLgrSeq": 14090896,
    "index": "9CA88CDEDFF9252B3DE183CE35B038F57282BC9503CDFA1923EF9A95DF0D6F7B",
}

signer_list_json = {
    "Flags": 0,
    "LedgerEntryType": "SignerList",
    "OwnerNode": "0000000000000000",
    "PreviousTxnID": "5904C0DC72C58A83AEFED2FFC5386356"
    "AA83FCA6A88C89D00646E51E687CDBE4",
    "PreviousTxnLgrSeq": 16061435,
    "SignerEntries": [
        {
            "SignerEntry": {
                "Account": "rsA2LpzuawewSBQXkiju3YQTMzW13pAAdW",
                "SignerWeight": 2,
            }
        },
        {
            "SignerEntry": {
                "Account": "raKEEVSGnKSD9Zyvxu4z6Pqpm4ABH8FS6n",
                "SignerWeight": 1,
            }
        },
        {
            "SignerEntry": {
                "Account": "rUpy3eEg8rqjqfUoLeBnZkscbKbFsKXC3v",
                "SignerWeight": 1,
            }
        },
    ],
    "SignerListID": 0,
    "SignerQuorum": 3,
    "index": "A9C28A28B85CD533217F5C0A0C7767666B093FA58A0F2D80026FCC4CD932DDC7",
}

ticket_json = {
    "Account": "rEhxGqkqPPSxQ3P25J66ft5TwpzV14k2de",
    "Flags": 0,
    "LedgerEntryType": "Ticket",
    "OwnerNode": "0000000000000000",
    "PreviousTxnID": "F19AD4577212D3BEACA0F75FE1BA1"
    "644F2E854D46E8D62E9C95D18E9708CBFB1",
    "PreviousTxnLgrSeq": 4,
    "TicketSequence": 3,
    "index": "A9C28A28B85CD533217F5C0A0C7767666B093FA58A0F2D80026FCC4CD932DDC7",
}

xchain_owned_claim_id_json = {
    "Account": "rBW1U7J9mEhEdk6dMHEFUjqQ7HW7WpaEMi",
    "Flags": 0,
    "OtherChainSource": "r9oXrvBX5aDoyMGkoYvzazxDhYoWFUjz8p",
    "OwnerNode": "0",
    "PreviousTxnID": "1CFD80E9CF232B8EED62A52857DE97438D12230C06496932A81DEFA6E660"
    "70A6",
    "PreviousTxnLgrSeq": 58673,
    "SignatureReward": "100",
    "XChainBridge": {
        "IssuingChainDoor": "rHb9CJAWyB4rj91VRWn96DkukG4bwdtyTh",
        "IssuingChainIssue": {"currency": "XRP"},
        "LockingChainDoor": "rMAXACCrp3Y8PpswXcg3bKggHX76V3F8M4",
        "LockingChainIssue": {"currency": "XRP"},
    },
    "XChainClaimAttestations": [
        {
            "XChainClaimProofSig": {
                "Amount": "1000000",
                "AttestationRewardAccount": "rfgjrgEJGDxfUY2U8VEDs7BnB1jiH3ofu6",
                "AttestationSignerAccount": "rfsxNxZ6xB1nTPhTMwQajNnkCxWG8B714n",
                "Destination": "rBW1U7J9mEhEdk6dMHEFUjqQ7HW7WpaEMi",
                "PublicKey": "025CA526EF20567A50FEC504589F949E0E3401C13EF76DD5FD1CC285"
                "0FA485BD7B",
                "WasLockingChainSend": 1,
            }
        },
        {
            "XChainClaimProofSig": {
                "Amount": "1000000",
                "AttestationRewardAccount": "rUUL1tP523M8KimERqVS7sxb1tLLmpndyv",
                "AttestationSignerAccount": "rEg5sHxZVTNwRL3BAdMwJatkmWDzHMmzDF",
                "Destination": "rBW1U7J9mEhEdk6dMHEFUjqQ7HW7WpaEMi",
                "PublicKey": "03D40434A6843638681E2F215310EBC4131AFB12EA85985DA073183B"
                "732525F7C9",
                "WasLockingChainSend": 1,
            },
        },
    ],
    "XChainClaimID": "b5",
    "LedgerEntryType": "XChainOwnedClaimID",
    "LedgerIndex": "20B136D7BF6D2E3D610E28E3E6BE09F5C8F4F0241BBF6E2D072AE1BACB1388F5",
}

xchain_owned_create_account_claim_id_json = {
    "Flags": 0,
    "LedgerEntryType": "XChainOwnedCreateAccountClaimID",
    "LedgerIndex": "5A92F6ED33FDA68FB4B9FD140EA38C056CD2BA9673ECA5B4CEF40F2166BB6F0C",
    "OwnerNode": "0",
    "PreviousTxnID": "1CFD80E9CF232B8EED62A52857DE97438D12230C06496932A81DEFA6E660",
    "PreviousTxnLgrSeq": 58673,
    "Account": "rHb9CJAWyB4rj91VRWn96DkukG4bwdtyTh",
    "XChainAccountCreateCount": "66",
    "XChainBridge": {
        "IssuingChainDoor": "rHb9CJAWyB4rj91VRWn96DkukG4bwdtyTh",
        "IssuingChainIssue": {"currency": "XRP"},
        "LockingChainDoor": "rMAXACCrp3Y8PpswXcg3bKggHX76V3F8M4",
        "LockingChainIssue": {"currency": "XRP"},
    },
    "XChainCreateAccountAttestations": [
        {
            "XChainCreateAccountProofSig": {
                "Amount": "20000000",
                "AttestationRewardAccount": "rMtYb1vNdeMDpD9tA5qSFm8WXEBdEoKKVw",
                "AttestationSignerAccount": "rL8qTrAvZ8Q1o1H9H9Ahpj3xjgmRvFLvJ3",
                "Destination": "rBW1U7J9mEhEdk6dMHEFUjqQ7HW7WpaEMi",
                "PublicKey": "021F7CC4033EFBE5E8214B04D1BAAEC14808DC6C02F4ACE930A8"
                "EF0F5909B0C438",
                "SignatureReward": "100",
                "WasLockingChainSend": 1,
            }
        }
    ],
}


class TestFromTODict(TestCase):
    def test_account_root(self):
        actual = LedgerObject.from_xrpl(account_root_json)
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
            domain="6D64756F31332E636F6D",
            email_hash="98B4375E1D753E5B91627516F6D70977",
            message_key="0000000000000000000000070000000300",
            nftoken_minter="rHello",
            transfer_rate=1004999999,
        )
        self.assertEqual(actual, expected)

    def test_amendments(self):
        actual = LedgerObject.from_xrpl(amendment_json)
        expected = Amendments(
            index="7DB0788C020F02780A673DC74757F23823FA3014C1866E72CC4CD8B226CD6EF4",
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

    def test_amm(self):
        actual = LedgerObject.from_xrpl(amm_json)
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
            owner_node="0",
            lp_token_balance=IssuedCurrencyAmount(
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

    def test_bridge(self):
        actual = LedgerObject.from_xrpl(bridge_json)
        expected = Bridge(
            account="r3nCVTbZGGYoWvZ58BcxDmiMUU7ChMa1eC",
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

    def test_check(self):
        actual = LedgerObject.from_xrpl(check_json)
        expected = Check(
            index="49647F0D748DC3FE26BDACBC57F251AADEFFF391403EC9BF87C97F67E9977FB0",
            account="rUn84CUYbNjRoTQ6mSW7BVJPSVJNLb1QLo",
            destination="rfkE1aSy9G8Upk4JssnwBxhEv5p4mn2KTy",
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
        )
        self.assertEqual(actual, expected)

    def test_deposit_preauth(self):
        actual = LedgerObject.from_xrpl(deposit_preauth_json)
        expected = DepositPreauth(
            index="4A255038CC3ADCC1A9C91509279B59908251728D0DAADB248FFE297D0F7E068C",
            account="rsUiUMpnrgxQp24dJYZDhmV4bE3aBtQyt8",
            authorize="rEhxGqkqPPSxQ3P25J66ft5TwpzV14k2de",
            owner_node="0000000000000000",
            previous_txn_id="3E8964D5A86B3CD6B9ECB33310D4E073D64C8"
            "65A5B866200AD2B7E29F8326702",
            previous_txn_lgr_seq=7,
        )
        self.assertEqual(actual, expected)

    def test_did(self):
        actual = LedgerObject.from_xrpl(did_json)
        expected = DID(
            account="rpfqJrXg5uidNo2ZsRhRY6TiF1cvYmV9Fg",
            did_document="646F63",
            data="617474657374",
            owner_node="0",
            previous_txn_id="A4C15DA185E6092DF5954FF62A1446220C61A5F60F0D93B4B09F"
            "708778E41120",
            previous_txn_lgr_seq=4,
            uri="6469645F6578616D706C65",
            index="46813BE38B798B3752CA590D44E7FEADB17485649074403AD1761A2835CE91FF",
        )
        self.assertEqual(actual, expected)

    def test_directory_node(self):
        actual = LedgerObject.from_xrpl(directory_node_json)
        expected = DirectoryNode(
            index="1BBEF97EDE88D40CEE2ADE6FEF121166AFE80D99EBADB01A4F069BA8FF484000",
            root_index="1BBEF97EDE88D40CEE2ADE6FEF121166A"
            "FE80D99EBADB01A4F069BA8FF484000",
            indexes=[
                "AD7EAE148287EF12D213A251015F86E6D4BD34B3C4A0A1ED9A17198373F908AD"
            ],
            exchange_rate="4F069BA8FF484000",
            taker_pays_currency="0000000000000000000000004A50590000000000",
            taker_pays_issuer="5BBC0F22F61D9224A110650CFE21CC0C4BE13098",
            taker_gets_currency="0000000000000000000000000000000000000000",
            taker_gets_issuer="0000000000000000000000000000000000000000",
        )
        self.assertEqual(actual, expected)

    def test_escrow(self):
        actual = LedgerObject.from_xrpl(escrow_json)
        expected = Escrow(
            index="DC5F3851D8A1AB622F957761E5963BC5BD439D5C24AC6AD7AC4523F0640244AC",
            account="rf1BiGeXwwQoi8Z2ueFYTEXSwuJYfV2Jpn",
            amount="10000",
            destination="ra5nK24KXen9AHvsdFTKHSANinZseWnPcX",
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

    def test_fee_settings(self):
        actual = LedgerObject.from_xrpl(fee_settings_json)
        expected = FeeSettings(
            index="4BC50C9B0D8515D3EAAE1E74B29A95804346C491EE1A95BF25E4AAB854A6A651",
            base_fee="000000000000000A",
            reference_fee_units=10,
            reserve_base=20000000,
            reserve_increment=5000000,
        )
        self.assertEqual(actual, expected)

    def test_ledger_hashes(self):
        actual = LedgerObject.from_xrpl(ledger_hashes_json)
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
        )
        self.assertEqual(actual, expected)

    def test_negative_unl(self):
        actual = LedgerObject.from_xrpl(negative_unl_json)
        expected = NegativeUNL(
            index="2E8A59AA9D3B5B186B0B9E0F62E6C02587CA74A4D778938E957B6357D364B244",
            disabled_validators=[
                DisabledValidator(
                    first_ledger_sequence=1609728,
                    public_key="ED6629D456285AE3613B285F65BBFF168D695BA"
                    "3921F309949AFCD2CA7AFEC16FE",
                )
            ],
        )
        self.assertEqual(actual, expected)

    def test_nftoken_offer(self):
        actual = LedgerObject.from_xrpl(nftoken_offer_json)
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

    def test_nftoken_page(self):
        actual = LedgerObject.from_xrpl(nftoken_page_json)
        expected = NFTokenPage(
            index="",
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

    def test_offer(self):
        actual = LedgerObject.from_xrpl(offer_json)
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
        )
        self.assertEqual(actual, expected)

    def test_pay_channel(self):
        actual = LedgerObject.from_xrpl(pay_channel_json)
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

    def test_ripple_state(self):
        actual = LedgerObject.from_xrpl(ripple_state_json)
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
        )
        self.assertEqual(actual, expected)

    def test_signer_list(self):
        actual = LedgerObject.from_xrpl(signer_list_json)
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

    def test_ticket(self):
        actual = LedgerObject.from_xrpl(ticket_json)
        expected = Ticket(
            index="A9C28A28B85CD533217F5C0A0C7767666B093FA58A0F2D80026FCC4CD932DDC7",
            account="rEhxGqkqPPSxQ3P25J66ft5TwpzV14k2de",
            flags=0,
            owner_node="0000000000000000",
            previous_txn_id="F19AD4577212D3BEACA0F75FE1BA1644F2E85"
            "4D46E8D62E9C95D18E9708CBFB1",
            previous_txn_lgr_seq=4,
            ticket_sequence=3,
        )
        self.assertEqual(actual, expected)

    def test_xchain_owned_claim_id(self):
        actual = LedgerObject.from_xrpl(xchain_owned_claim_id_json)
        expected = XChainOwnedClaimID(
            account="rBW1U7J9mEhEdk6dMHEFUjqQ7HW7WpaEMi",
            other_chain_source="r9oXrvBX5aDoyMGkoYvzazxDhYoWFUjz8p",
            owner_node="0",
            previous_txn_id="1CFD80E9CF232B8EED62A52857DE97438D12230C06496932A81DEFA6E6"
            "6070A6",
            previous_txn_lgr_seq=58673,
            signature_reward="100",
            xchain_bridge=XChainBridge(
                issuing_chain_door="rHb9CJAWyB4rj91VRWn96DkukG4bwdtyTh",
                issuing_chain_issue=XRP(),
                locking_chain_door="rMAXACCrp3Y8PpswXcg3bKggHX76V3F8M4",
                locking_chain_issue=XRP(),
            ),
            xchain_claim_attestations=[
                XChainClaimProofSig(
                    amount="1000000",
                    attestation_reward_account="rfgjrgEJGDxfUY2U8VEDs7BnB1jiH3ofu6",
                    attestation_signer_account="rfsxNxZ6xB1nTPhTMwQajNnkCxWG8B714n",
                    destination="rBW1U7J9mEhEdk6dMHEFUjqQ7HW7WpaEMi",
                    public_key="025CA526EF20567A50FEC504589F949E0E3401C13EF76DD5FD1CC2"
                    "850FA485BD7B",
                    was_locking_chain_send=1,
                ),
                XChainClaimProofSig(
                    amount="1000000",
                    attestation_reward_account="rUUL1tP523M8KimERqVS7sxb1tLLmpndyv",
                    attestation_signer_account="rEg5sHxZVTNwRL3BAdMwJatkmWDzHMmzDF",
                    destination="rBW1U7J9mEhEdk6dMHEFUjqQ7HW7WpaEMi",
                    public_key="03D40434A6843638681E2F215310EBC4131AFB12EA85985DA07318"
                    "3B732525F7C9",
                    was_locking_chain_send=1,
                ),
            ],
            xchain_claim_id="b5",
            ledger_index="20B136D7BF6D2E3D610E28E3E6BE09F5C8F4F0241BBF6E2D072AE1BACB13"
            "88F5",
        )
        self.assertEqual(actual, expected)

    def test_xchain_owned_create_account_claim_id(self):
        actual = LedgerObject.from_xrpl(xchain_owned_create_account_claim_id_json)
        expected = XChainOwnedCreateAccountClaimID(
            account="rHb9CJAWyB4rj91VRWn96DkukG4bwdtyTh",
            owner_node="0",
            previous_txn_id="1CFD80E9CF232B8EED62A52857DE97438D12230C06496932A81D"
            "EFA6E660",
            previous_txn_lgr_seq=58673,
            ledger_index="5A92F6ED33FDA68FB4B9FD140EA38C056CD2BA9673ECA5B4CEF40F2166B"
            "B6F0C",
            xchain_account_create_count="66",
            xchain_bridge=XChainBridge(
                issuing_chain_door="rHb9CJAWyB4rj91VRWn96DkukG4bwdtyTh",
                issuing_chain_issue=XRP(),
                locking_chain_door="rMAXACCrp3Y8PpswXcg3bKggHX76V3F8M4",
                locking_chain_issue=XRP(),
            ),
            xchain_create_account_attestations=[
                XChainCreateAccountProofSig(
                    amount="20000000",
                    attestation_reward_account="rMtYb1vNdeMDpD9tA5qSFm8WXEBdEoKKVw",
                    attestation_signer_account="rL8qTrAvZ8Q1o1H9H9Ahpj3xjgmRvFLvJ3",
                    destination="rBW1U7J9mEhEdk6dMHEFUjqQ7HW7WpaEMi",
                    public_key="021F7CC4033EFBE5E8214B04D1BAAEC14808DC6C02F4ACE930A8E"
                    "F0F5909B0C438",
                    signature_reward="100",
                    was_locking_chain_send=1,
                )
            ],
        )
        self.assertEqual(actual, expected)
