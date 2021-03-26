"""The information needed to control an XRPL account."""

from __future__ import annotations

from typing import Type

from xrpl import CryptoAlgorithm
from xrpl.core.keypairs import derive_classic_address, derive_keypair, generate_seed


class Wallet:
    """
    The cryptographic keys needed to control an XRP Ledger account. See
    `Cryptographic Keys <https://xrpl.org/cryptographic-keys.html>`_ for
    details.
    """

    def __init__(self: Wallet, seed: str) -> None:
        """
        Generate a new Wallet.

        Args:
            seed: The seed from which the public and private keys are derived.
        """
        #: The core value that is used to derive all other information about
        #: this wallet. MUST be kept secret!
        self.seed = seed

        pk, sk = derive_keypair(self.seed)
        #: The public key that is used to identify this wallet's signatures, as
        #: a hexadecimal string.
        self.pub_key = pk
        #: The private key that is used to create signatures, as a hexadecimal
        #: string. MUST be kept secret!
        self.priv_key = sk

        #: The address that publicly identifies this wallet, as a base58 string.
        self.classic_address = derive_classic_address(self.pub_key)

        #: The next available sequence number to use for transactions from this
        #: wallet. Must be updated by the user.
        self.next_sequence_num = 0

    @classmethod
    def create(
        cls: Type[Wallet], crypto_algorithm: CryptoAlgorithm = CryptoAlgorithm.SECP256K1
    ) -> Wallet:
        """
        Generates a new seed and Wallet.

        Args:
            crypto_algorithm: The key-generation algorithm to use when generating the
                seed. The default is secp256k1.

        Returns:
            The wallet that is generated from the given seed.
        """
        seed = generate_seed(algorithm=crypto_algorithm)
        return cls(seed)

    def __str__(self: Wallet) -> str:
        """
        Returns a string representation of a Wallet.

        Returns:
            A string representation of a Wallet.
        """
        return (
            f"seed: {self.seed}\npub_key: {self.pub_key}\n"
            f"priv_key: {self.priv_key}\nclassic_address: {self.classic_address}\n"
        )
