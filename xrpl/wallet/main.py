"""The information needed to control an XRPL account."""

from __future__ import annotations

from typing import Optional, Type

from xrpl.constants import CryptoAlgorithm
from xrpl.core.addresscodec import classic_address_to_xaddress
from xrpl.core.keypairs import derive_classic_address, derive_keypair, generate_seed
from xrpl.utils.ensure_classic_address import ensure_classic_address


class Wallet:
    """
    The cryptographic keys needed to control an XRP Ledger account. See
    `Cryptographic Keys <https://xrpl.org/cryptographic-keys.html>`_ for
    details.
    """

    @property
    def address(self: Wallet) -> str:
        """
        Alias for wallet.classic_address.

        Returns:
            The address that publicly identifies this wallet, as a base58 string.
        """
        return self.classic_address

    @address.setter
    def address(self: Wallet, value: str) -> None:
        """
        Setter for address that reflects in classic_address.

        Args:
            value: New value for address/classic_address.
        """
        self.classic_address = value

    def __init__(
        self: Wallet,
        seed: Optional[str] = None,
        sequence: Optional[int] = 0,
        *,
        algorithm: Optional[CryptoAlgorithm] = None,
        master_address: Optional[str] = None,
    ) -> None:
        """
        Generate a new Wallet.

        Args:
            seed: The seed from which the public and private keys are derived.
                Generates a new seed if not included.
            sequence: The next sequence number for the account. Defaulted to 0 if not
                included.
            algorithm: The algorithm used to encode the keys. Inferred from the seed if
                not included. The default is None.
            master_address: Include if a Wallet uses a Regular Key Pair. It must be
                the master address of the account. The default is `None`.
        """
        if seed is None:
            if algorithm is None:
                seed = generate_seed()
            else:
                seed = generate_seed(algorithm=algorithm)
        self.seed: Optional[str] = seed
        """
        The core value that is used to derive all other information about
        this wallet. MUST be kept secret!
        """

        pk, sk = derive_keypair(self.seed, algorithm=algorithm)
        self.public_key = pk
        """
        The public key that is used to identify this wallet's signatures, as
        a hexadecimal string.
        """

        self.private_key = sk
        """
        The private key that is used to create signatures, as a hexadecimal
        string. MUST be kept secret!
        """

        self.classic_address = (
            ensure_classic_address(master_address)
            if master_address is not None
            else derive_classic_address(self.public_key)
        )
        """The address that publicly identifies this wallet, as a base58 string."""

        self.sequence = sequence
        """
        The next available sequence number to use for transactions from this
        wallet.
        Must be updated by the user. Increments on the ledger with every successful
        transaction submission, and stays the same with every failed transaction
        submission.
        """

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
        return cls(algorithm=crypto_algorithm)

    @classmethod
    def from_public_private_keys(
        cls: Type[Wallet],
        public_key: str,
        private_key: str,
        master_address: Optional[str] = None,
    ) -> Wallet:
        """
        Generates a new Wallet from public and private keys.

        Args:
            public_key: The public key for the account.
            private_key: The private key used for signing transactions for the account.
            master_address: Include if a Wallet uses a Regular Key Pair. It must be
                the master address of the account. The default is `None`.

        Returns:
            The wallet that is generated from the given keys.
        """
        wallet = cls()
        wallet.seed = None
        wallet.public_key = public_key
        wallet.private_key = private_key
        wallet.classic_address = (
            ensure_classic_address(master_address)
            if master_address is not None
            else derive_classic_address(public_key)
        )
        return wallet

    @classmethod
    def from_seed(
        cls: Type[Wallet],
        seed: str,
        master_address: Optional[str] = None,
        crypto_algorithm: CryptoAlgorithm = CryptoAlgorithm.ED25519,
    ) -> Wallet:
        """
        Generates a new Wallet from seed.

        Args:
            seed: The seed (secret) used to derive the account keys.
            master_address: Include if a Wallet uses a Regular Key Pair. It must be
                the master address of the account. The default is `None`.
            crypto_algorithm: The key-generation algorithm to use when generating the
                seed. The default is Ed25519.

        Returns:
            The wallet that is generated from the given secret.
        """
        return cls(seed, master_address=master_address, algorithm=crypto_algorithm)

    from_secret = from_seed

    @classmethod
    def from_entropy(
        cls: Type[Wallet],
        entropy: str,
        master_address: Optional[str] = None,
        crypto_algorithm: CryptoAlgorithm = CryptoAlgorithm.ED25519,
    ) -> Wallet:
        """
        Generates a new Wallet from entropy (array of random numbers).

        Args:
            entropy: A string of random numbers to generate a seed used to derive
                a wallet.
            master_address: Include if a Wallet uses a Regular Key Pair. It must be
                the master address of the account. The default is `None`.
            crypto_algorithm: The key-generation algorithm to use when generating the
                seed. The default is Ed25519.

        Returns:
            The wallet that is generated from the given entropy.
        """
        return cls(
            generate_seed(entropy=entropy, algorithm=crypto_algorithm),
            algorithm=crypto_algorithm,
            master_address=master_address,
        )

    def get_xaddress(
        self: Wallet, *, tag: Optional[int] = None, is_test: bool = False
    ) -> str:
        """
        Returns the X-Address of the Wallet's account.

        Args:
            tag: the destination tag of the address. Defaults to `None`.
            is_test: whether the address corresponds to an address on the test network.

        Returns:
            The X-Address of the Wallet's account.
        """
        return classic_address_to_xaddress(self.classic_address, tag, is_test)

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
