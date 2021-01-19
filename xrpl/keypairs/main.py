"""Public interface for keypairs module"""
from random import randbytes
from xrpl import addresscodec, CryptoAlgorithm
from xrpl.keypairs import ed25519, secp256k1, exceptions, helpers

_ALGORITHM_TO_MODULE_MAP = {
    CryptoAlgorithm.ED25519: ed25519,
    CryptoAlgorithm.SECP256K1: secp256k1,
}
# Ensure all CryptoAlgorithms have a module
assert len(_ALGORITHM_TO_MODULE_MAP) == len(CryptoAlgorithm)

_VERIFICATION_MESSAGE = helpers._sha512_first_half(b"This test message should verify.")


def generate_seed(entropy=None, algorithm=CryptoAlgorithm.ED25519):
    """
    entropy: string, must be at least addresscodec.SEED_LENGTH bytes long and
    will be truncated to that length
    algorithm: any of CryptoAlgorithm

    returns: string, a seed suitable for use with derive
    """
    if entropy is None:
        entropy = randbytes(addresscodec.SEED_LENGTH)
    else:
        entropy = entropy[: addresscodec.SEED_LENGTH]
    return addresscodec.encode_seed(entropy, algorithm)


def derive(seed):
    """
    TODO: annotate and determine how keys can be made optional
    returns: (public_key: string, private_key: string)
    """
    decoded_entropy, algorithm = addresscodec.decode_seed(seed)
    module = _ALGORITHM_TO_MODULE_MAP[algorithm]
    public_key, private_key = module.derive(decoded_entropy)
    signature = module.sign(_VERIFICATION_MESSAGE, private_key)
    if not module.is_valid(_VERIFICATION_MESSAGE, signature, public_key):
        raise exceptions.KeypairException(
            "derived keypair did not generate verifiable signature",
        )
    return public_key, private_key
