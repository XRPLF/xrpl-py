"""Public interface for keypairs module."""
from random import randbytes
from typing import Any, Dict, Final, Optional, Tuple

from xrpl import CryptoAlgorithm, addresscodec
from xrpl.keypairs import ed25519, secp256k1
from xrpl.keypairs.exceptions import KeypairException
from xrpl.keypairs.helpers import sha512_first_half

# TODO: need to determine interface strategy for these modules, which will
# effect the type used here, allowing us to remove the Any
_ALGORITHM_TO_MODULE_MAP: Final[Dict[CryptoAlgorithm, Any]] = {
    CryptoAlgorithm.ED25519: ed25519,
    CryptoAlgorithm.SECP256K1: secp256k1,
}
# Ensure all CryptoAlgorithms have a module
assert len(_ALGORITHM_TO_MODULE_MAP) == len(CryptoAlgorithm)

_VERIFICATION_MESSAGE: Final[bytes] = sha512_first_half(
    b"This test message should verify."
)


def generate_seed(
    entropy: Optional[str] = None,
    algorithm: CryptoAlgorithm = CryptoAlgorithm.ED25519,
) -> str:
    """
    entropy: must be at least addresscodec.SEED_LENGTH bytes long and
    will be truncated to that length
    algorithm: CryptoAlgorithm to use for seed generation

    returns: a seed suitable for use with derive
    """
    parsed_entropy = (
        randbytes(addresscodec.SEED_LENGTH)
        if entropy is None
        else entropy[: addresscodec.SEED_LENGTH]
    )
    return addresscodec.encode_seed(parsed_entropy, algorithm)


def derive(seed: str) -> Tuple[str, str]:
    """
    Given seed, which can be generated via `generate_seed`, returns
    public and private keypair.
    seed: value from which to derive keypair
    returns: (public_key, private_key) keypair
    """
    decoded_seed, algorithm = addresscodec.decode_seed(seed)
    module = _ALGORITHM_TO_MODULE_MAP[algorithm]
    public_key, private_key = module.derive(decoded_seed)
    signature = module.sign(_VERIFICATION_MESSAGE, private_key)
    if not module.is_message_valid(_VERIFICATION_MESSAGE, signature, public_key):
        raise KeypairException(
            "derived keypair did not generate verifiable signature",
        )
    return public_key, private_key
