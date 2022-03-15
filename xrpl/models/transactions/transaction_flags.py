"""All transacion flags."""

from typing import Dict, Tuple

TX_FLAG_PREFIXES: Tuple[str, str, str, str] = (
    "Asf",
    "Tf",
    "asf_",
    "tf_",
)

TX_FLAGS: Dict[str, Dict[str, int]] = {
    "AccountDelete": {},
    "AccountSet": {
        "asf_account_tx_id": 5,
        "asf_authorized_minter": 10,
        "asf_default_ripple": 8,
        "asf_deposit_auth": 9,
        "asf_disable_master": 4,
        "asf_disallow_xrp": 3,
        "asf_global_freeze": 7,
        "asf_no_freeze": 6,
        "asf_require_auth": 2,
        "asf_require_dest": 1,
    },
    "CheckCancel": {},
    "CheckCash": {},
    "CheckCreate": {},
    "DepositPreauth": {},
    "EscrowCancel": {},
    "EscrowCreate": {},
    "EscrowFinish": {},
    "NFTokenAcceptOffer": {},
    "NFTokenBurn": {},
    "NFTokenCancelOffer": {},
    "NFTokenCreateOffer": {
        "tf_sell_token": 0x00000001,
    },
    "NFTokenMint": {
        "tf_burnable": 0x00000001,
        "tf_only_xrp": 0x00000002,
        "tf_trustline": 0x00000004,
        "tf_transferable": 0x00000008,
    },
    "OfferCancel": {},
    "OfferCreate": {
        "tf_passive": 0x00010000,
        "tf_immediate_or_cancel": 0x00020000,
        "tf_fill_or_kill": 0x00040000,
        "tf_sell": 0x00080000,
    },
    "Payment": {
        "tf_no_direct_ripple": 0x00010000,
        "tf_partial_payment": 0x00020000,
        "tf_limit_quality": 0x00040000,
    },
    "PaymentChannelClaim": {
        "tf_renew": 0x00010000,
        "tf_close": 0x00020000,
    },
    "PaymentChannelCreate": {},
    "PaymentChannelFund": {},
    "SetRegularKey": {},
    "SignerListSet": {},
    "TicketCreate": {},
    "TrustSet": {
        "tf_set_auth": 0x00010000,
        "tf_set_no_ripple": 0x00020000,
        "tf_clear_no_ripple": 0x00040000,
        "tf_set_freeze": 0x00100000,
        "tf_clear_freeze": 0x00200000,
    },
    "EnableAmendment": {
        "tf_got_majority": 0x00010000,
        "tf_lost_majority": 0x00020000,
    },
    "SetFee": {},
    "UNLModify": {},
}
