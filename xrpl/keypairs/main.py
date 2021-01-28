"""Public interface for keypairs module."""
from secrets import token_bytes
from typing import Any, Dict, Optional, Tuple

from typing_extensions import Final

from xrpl import CryptoAlgorithm, addresscodec
from xrpl.keypairs import ed25519, secp256k1
from xrpl.keypairs.exceptions import XRPLKeypairsException
from xrpl.keypairs.helpers import sha512_first_half

# using Any type here because the overhead of an abstract class for these two
# modules would be overkill and we'll raise in tests if they do not satisfy
# the implicit interface
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
    if entropy is None:
        parsed_entropy = token_bytes(addresscodec.SEED_LENGTH)
    else:
        parsed_entropy = bytes(entropy, "UTF-8")[: addresscodec.SEED_LENGTH]
    return addresscodec.encode_seed(parsed_entropy, algorithm)


def derive_keypair(seed: str, validator: bool = False) -> Tuple[str, str]:
    """
    Given seed, which can be generated via `generate_seed`, returns
    public and private keypair.
    seed: value from which to derive keypair
    returns: (public_key, private_key) keypair
    """
    decoded_seed, algorithm = addresscodec.decode_seed(seed)
    module = _ALGORITHM_TO_MODULE_MAP[algorithm]
    public_key, private_key = module.derive_keypair(decoded_seed, validator)
    signature = module.sign(_VERIFICATION_MESSAGE, private_key)
    if not module.is_message_valid(_VERIFICATION_MESSAGE, signature, public_key):
        raise XRPLKeypairsException(
            "Derived keypair did not generate verifiable signature",
        )
    return public_key, private_key
