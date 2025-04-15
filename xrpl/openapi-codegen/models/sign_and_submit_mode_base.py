"""Model for SignAndSubmitModeBase."""

from dataclasses import dataclass
from typing import Optional
from xrpl.models.base_model import BaseModel
from xrpl.models.utils import require_kwargs_on_init


@require_kwargs_on_init
@dataclass(frozen=True)
class SignAndSubmitModeBase(BaseModel):
    """
    A mode for signing a transaction and immediately submitting it. This mode is intended
    for testing.
    """

    secret: Optional[str] = None
    """
    (Optional) Secret key of the account supplying the transaction, used to sign it. Do not
    send your secret to untrusted servers or through unsecured network connections. Cannot
    be used with key_type, seed, seed_hex, or passphrase.
    """

    seed: Optional[str] = None
    """
    (Optional) Secret key of the account supplying the transaction, used to sign it. Must be
    in the XRP Ledger's base58 format. If provided, you must also specify the key_type.
    Cannot be used with secret, seed_hex, or passphrase.
    """

    seed_hex: Optional[str] = None
    """
    (Optional) Secret key of the account supplying the transaction, used to sign it. Must be
    in hexadecimal format. If provided, you must also specify the key_type. Cannot be used
    with secret, seed, or passphrase.
    """

    passphrase: Optional[str] = None
    """
    (Optional) Secret key of the account supplying the transaction, used to sign it, as a
    string passphrase. If provided, you must also specify the key_type. Cannot be used with
    secret, seed, or seed_hex.
    """

    key_type: Optional[str] = None
    """
    (Optional) Type of cryptographic key provided in this request. Valid types are secp256k1
    or ed25519. Defaults to secp256k1. Cannot be used with secret. Caution: Ed25519 support
    is experimental.
    """

    fail_hard: Optional[bool] = None
    """
    (Optional) If true, and the transaction fails locally, do not retry or relay the
    transaction to other servers. Default is false. Updated in: rippled 1.5.0
    """

    offline: Optional[bool] = None
    """
    (Optional) If true, when constructing the transaction, do not try to automatically fill
    in or validate values. Default is false.
    """

    build_path: Optional[bool] = None
    """
    (Optional) If this field is provided, the server auto-fills the Paths field of a Payment
    transaction before signing. Omit this field if the transaction is a direct XRP payment
    or if it is not a Payment-type transaction. Caution: The server looks for the presence
    or absence of this field, not its value. This behavior may change. (Issue #3272)
    """

    fee_mult_max: Optional[int] = None
    """
    (Optional) Sign-and-submit fails with the error rpcHIGH_FEE if the auto-filled Fee value
    would be greater than the reference transaction cost x fee_mult_max ÷ fee_div_max. This
    field has no effect if you explicitly specify the Fee field of the transaction. Default
    is 10.
    """

    fee_div_max: Optional[int] = None
    """
    (Optional) Sign-and-submit fails with the error rpcHIGH_FEE if the auto-filled Fee value
    would be greater than the reference transaction cost x fee_mult_max ÷ fee_div_max. This
    field has no effect if you explicitly specify the Fee field of the transaction. Default
    is 1.
    """
