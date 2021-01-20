"""Public interface for keypairs module"""

import hashlib
import random
from xrpl import addresscodec


def _hash(message):
    """Fundamental method, returning
    hash of input.

    :param message: input to hash
    :returns hash of message
    """
    hasher = hashlib.sha512()
    hasher.update(bytes(str(message), "UTF-8"))
    return hasher.digest()[:32]


def generate_seed(entropy=None, algorithm=addresscodec.ED25519):
    """
    entropy: string, must be at least addresscodec.SEED_LENGTH bytes long and
    will be truncated to that length
    algorithm: any of addresscodec.ALGORITHMS

    returns: string, a seed suitable for use with derive_keypair
    """
    if entropy is None:
        entropy = random.randbytes(addresscodec.SEED_LENGTH)
    else:
        entropy = entropy[: addresscodec.SEED_LENGTH]
    return addresscodec.encode_seed(entropy, algorithm)
