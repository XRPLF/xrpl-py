"""The information needed to control an XRPL account."""

from __future__ import annotations

from typing import Type

from xrpl.constants import CryptoAlgorithm
from xrpl.core.keypairs import derive_classic_address, derive_keypair, generate_seed


class Wallet:
    """
    The cryptographic keys needed to control an XRP Ledger account. See
    `Cryptographic Keys <https://xrpl.org/cryptographic-keys.html>`_ for
    details.
    """

    def __init__(self: Wallet, seed: str, sequence: int) -> None:
        """
        Generate a new Wallet.

        Args:
            seed: The seed from which the public and private keys are derived.
            sequence: The next sequence number for the account.
        """
        #: The core value that is used to derive all other information about
        #: this wallet. MUST be kept secret!
        self.seed = seed

        pk, sk = derive_keypair(self.seed)
        #: The public key that is used to identify this wallet's signatures, as
        #: a hexadecimal string.
        self.public_key = pk
        #: The private key that is used to create signatures, as a hexadecimal
        #: string. MUST be kept secret!
        self.private_key = sk

        #: The address that publicly identifies this wallet, as a base58 string.
        self.classic_address = derive_classic_address(self.public_key)

        #: The next available sequence number to use for transactions from this
        #: wallet.
        #: Must be updated by the user. Increments on the ledger with every successful
        #: transaction submission, and stays the same with every failed transaction
        #: submission.
        self.sequence = sequence

    @classmethod
    def create(
        cls: Type[Wallet], crypto_algorithm: CryptoAlgorithm = CryptoAlgorithm.ED25519
    ) -> Wallet:
        """
        Generates a new seed and Wallet.

        Args:
            crypto_algorithm: The key-generation algorithm to use when generating the
                seed. The default is Ed25519.

        Returns:
            The wallet that is generated from the given seed.
        """
        seed = generate_seed(algorithm=crypto_algorithm)
        return cls(seed, sequence=0)

    def __str__(self: Wallet) -> str:
        """
        Returns a string representation of a Wallet.

        Returns:
            A string representation of a Wallet.
        """
        return "\n".join(
            [
                f"public_key: {self.public_key}",
                "private_key: -HIDDEN-",
                f"classic_address: {self.classic_address}",
            ]
        )
