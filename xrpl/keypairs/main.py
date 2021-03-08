"""Public interface for keypairs module."""
from secrets import token_bytes
from typing import Dict, Optional, Tuple, Type

from typing_extensions import Final

from xrpl import CryptoAlgorithm, addresscodec
from xrpl.keypairs.crypto_implementation import CryptoImplementation
from xrpl.keypairs.ed25519 import ED25519
from xrpl.keypairs.ed25519 import PREFIX as ED_PREFIX
from xrpl.keypairs.exceptions import XRPLKeypairsException
from xrpl.keypairs.helpers import get_account_id
from xrpl.keypairs.secp256k1 import SECP256K1

_VERIFICATION_MESSAGE: Final[bytes] = b"This test message should verify."

_ALGORITHM_TO_MODULE_MAP: Final[Dict[CryptoAlgorithm, Type[CryptoImplementation]]] = {
    CryptoAlgorithm.ED25519: ED25519,
    CryptoAlgorithm.SECP256K1: SECP256K1,
}


def generate_seed(
    entropy: Optional[str] = None,
    algorithm: CryptoAlgorithm = CryptoAlgorithm.ED25519,
) -> str:
    """
    Generates a seed suitable for use with derive.

    Args:
        entropy: Must be at least addresscodec.SEED_LENGTH bytes long and
            will be truncated to that length
        algorithm: CryptoAlgorithm to use for seed generation

    Returns:
        A seed suitable for use with derive
    """
    if entropy is None:
        parsed_entropy = token_bytes(addresscodec.SEED_LENGTH)
    else:
        parsed_entropy = bytes(entropy, "UTF-8")[: addresscodec.SEED_LENGTH]
    return addresscodec.encode_seed(parsed_entropy, algorithm)


def derive_keypair(seed: str, validator: bool = False) -> Tuple[str, str]:
    """
    Given seed, which can be generated via `generate_seed`, returns
    public and private keypair.

    Args:
        seed: Value from which to derive keypair
        validator: Whether the keypair is a validator keypair.

    Returns:
        A public and private keypair.

    Raises:
        XRPLKeypairsException: If the derived keypair did not generate a
            verifiable signature.
    """
    decoded_seed, algorithm = addresscodec.decode_seed(seed)
    module = _ALGORITHM_TO_MODULE_MAP[algorithm]
    public_key, private_key = module.derive_keypair(decoded_seed, validator)
    signature = module.sign(str(_VERIFICATION_MESSAGE), private_key)
    if not module.is_valid_message(str(_VERIFICATION_MESSAGE), signature, public_key):
        raise XRPLKeypairsException(
            "Derived keypair did not generate verifiable signature",
        )
    return public_key, private_key


def derive_classic_address(public_key: str) -> str:
    """
    Returns the classic address for the given public key. See
    https://xrpl.org/cryptographic-keys.html#account-id-and-address
    for more information.

    Args:
        public_key: Public key from which to derive address.

    Returns:
        Classic address corresponding to public key.
    """
    account_id = get_account_id(bytes.fromhex(public_key))
    return addresscodec.encode_classic_address(account_id)


def sign(message: bytes, private_key: str) -> str:
    """
    Given message and private key returns signed message.

    Args:
        message: Message to sign.
        private_key: Private key generated using any of the supported
            CryptoAlgorithm.

    Returns:
        Signed message.
    """
    return (
        _get_module_from_key(private_key)
        .sign(
            str(message),
            private_key,
        )
        .hex()
        .upper()
    )


def is_valid_message(message: bytes, signature: bytes, public_key: str) -> bool:
    """
    Returns True if message is valid given signature and public key.

    Args:
        message: Message to check against signature.
        signature: Signature of message as created with private key.
        public_key: Public key corresponding to private key used to generate
            signature.

    Returns:
        True if message is valid given signature and public key.
    """
    return _get_module_from_key(public_key).is_valid_message(
        str(message),
        signature,
        public_key,
    )


def _get_module_from_key(key: str) -> Type[CryptoImplementation]:
    if key.startswith(ED_PREFIX):
        return ED25519
    return SECP256K1
