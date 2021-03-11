"""The information needed to control an XRPL account."""

from __future__ import annotations

from typing import Type

from xrpl import CryptoAlgorithm
from xrpl.keypairs import derive_classic_address, derive_keypair, generate_seed


class Wallet:
    """The information needed to control an XRPL account."""

    def __init__(self: Wallet, seed: str) -> None:
        """
        Generate a new Wallet.

        Args:
            seed: The seed from which the public and private keys are derived.
        """
        self.seed = seed
        self.pub_key, self.priv_key = derive_keypair(self.seed)
        self.classic_address = derive_classic_address(self.pub_key)
        self.next_sequence_num = 0

    @classmethod
    def generate_seed_and_wallet(
        cls: Type[Wallet], crypto_algorithm: CryptoAlgorithm = CryptoAlgorithm.SECP256K1
    ) -> Wallet:
        """
        Generates a new seed and Wallet.

        Args:
            crypto_algorithm: The key-generation algorithm to use when generating the
                seed. Defaults to SECP256K1.

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
