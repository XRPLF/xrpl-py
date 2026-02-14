"""
Build script for mpt-crypto C library Python bindings using cffi.
"""

import os
import platform

from cffi import FFI

ffibuilder = FFI()

# Define the C API that we want to expose to Python
ffibuilder.cdef(
    """
    // Opaque types from secp256k1
    typedef struct secp256k1_context_struct secp256k1_context;
    typedef struct {
        unsigned char data[64];
    } secp256k1_pubkey;
    
    // Context creation/destruction
    secp256k1_context* secp256k1_context_create(unsigned int flags);
    void secp256k1_context_destroy(secp256k1_context* ctx);
    
    // Public key serialization
    int secp256k1_ec_pubkey_serialize(
        const secp256k1_context* ctx,
        unsigned char *output,
        size_t *outputlen,
        const secp256k1_pubkey* pubkey,
        unsigned int flags
    );
    
    int secp256k1_ec_pubkey_parse(
        const secp256k1_context* ctx,
        secp256k1_pubkey* pubkey,
        const unsigned char *input,
        size_t inputlen
    );
    
    // ElGamal operations
    int secp256k1_elgamal_generate_keypair(
        const secp256k1_context* ctx,
        unsigned char* privkey,
        secp256k1_pubkey* pubkey
    );
    
    int secp256k1_elgamal_encrypt(
        const secp256k1_context* ctx,
        secp256k1_pubkey* c1,
        secp256k1_pubkey* c2,
        const secp256k1_pubkey* pubkey_Q,
        uint64_t amount,
        const unsigned char* blinding_factor
    );
    
    int secp256k1_elgamal_decrypt(
        const secp256k1_context* ctx,
        uint64_t* amount,
        const secp256k1_pubkey* c1,
        const secp256k1_pubkey* c2,
        const unsigned char* privkey
    );
    
    // Proof of Knowledge of Secret Key
    int secp256k1_mpt_pok_sk_prove(
        const secp256k1_context* ctx,
        unsigned char* proof,
        const secp256k1_pubkey* pk,
        const unsigned char* sk,
        const unsigned char* context_id
    );
    
    int secp256k1_mpt_pok_sk_verify(
        const secp256k1_context* ctx,
        const unsigned char* proof,
        const secp256k1_pubkey* pk,
        const unsigned char* context_id
    );
    
    // Canonical encrypted zero
    int generate_canonical_encrypted_zero(
        const secp256k1_context* ctx,
        secp256k1_pubkey* enc_zero_c1,
        secp256k1_pubkey* enc_zero_c2,
        const secp256k1_pubkey* pubkey,
        const unsigned char* account_id,
        const unsigned char* mpt_issuance_id
    );
    
    // Equality proof (knowledge of plaintext and randomness)
    int secp256k1_equality_plaintext_prove(
        const secp256k1_context* ctx,
        unsigned char* proof,
        const secp256k1_pubkey* c1,
        const secp256k1_pubkey* c2,
        const secp256k1_pubkey* pk_recipient,
        uint64_t amount,
        const unsigned char* randomness_r,
        const unsigned char* tx_context_id
    );
    
    int secp256k1_equality_plaintext_verify(
        const secp256k1_context* ctx,
        const unsigned char* proof,
        const secp256k1_pubkey* c1,
        const secp256k1_pubkey* c2,
        const secp256k1_pubkey* pk_recipient,
        uint64_t amount,
        const unsigned char* tx_context_id
    );
    
    // Same plaintext proof (two ciphertexts)
    int secp256k1_mpt_prove_same_plaintext(
        const secp256k1_context* ctx,
        unsigned char* proof_out,
        const secp256k1_pubkey* R1, const secp256k1_pubkey* S1, const secp256k1_pubkey* P1,
        const secp256k1_pubkey* R2, const secp256k1_pubkey* S2, const secp256k1_pubkey* P2,
        uint64_t amount_m,
        const unsigned char* randomness_r1,
        const unsigned char* randomness_r2,
        const unsigned char* tx_context_id
    );
    
    int secp256k1_mpt_verify_same_plaintext(
        const secp256k1_context* ctx,
        const unsigned char* proof,
        const secp256k1_pubkey* R1, const secp256k1_pubkey* S1, const secp256k1_pubkey* P1,
        const secp256k1_pubkey* R2, const secp256k1_pubkey* S2, const secp256k1_pubkey* P2,
        const unsigned char* tx_context_id
    );

    // Pedersen Commitment
    int secp256k1_mpt_pedersen_commit(
        const secp256k1_context* ctx,
        secp256k1_pubkey* commitment,
        uint64_t amount,
        const unsigned char* blinding_factor_rho
    );

    // Bulletproof (Range Proof)
    int secp256k1_bulletproof_prove(
        const secp256k1_context* ctx,
        unsigned char* proof_out,
        size_t* proof_len,
        uint64_t value,
        const unsigned char* blinding_factor,
        const secp256k1_pubkey* pk_base,
        unsigned int proof_type
    );

    int secp256k1_bulletproof_verify(
        const secp256k1_context* ctx,
        const unsigned char* proof,
        size_t proof_len,
        const secp256k1_pubkey* commitment_C,
        const secp256k1_pubkey* pk_base
    );

    // ElGamal-Pedersen Link Proof
    int secp256k1_elgamal_pedersen_link_prove(
        const secp256k1_context* ctx,
        unsigned char* proof,
        const secp256k1_pubkey* c1,
        const secp256k1_pubkey* c2,
        const secp256k1_pubkey* pk,
        const secp256k1_pubkey* pcm,
        uint64_t amount,
        const unsigned char* r,
        const unsigned char* rho,
        const unsigned char* context_id
    );

    int secp256k1_elgamal_pedersen_link_verify(
        const secp256k1_context* ctx,
        const unsigned char* proof,
        const secp256k1_pubkey* c1,
        const secp256k1_pubkey* c2,
        const secp256k1_pubkey* pk,
        const secp256k1_pubkey* pcm,
        const unsigned char* context_id
    );

    // Proof of same plaintext (multi-ciphertext)
    size_t secp256k1_mpt_prove_same_plaintext_multi_size(size_t n_ciphertexts);

    int secp256k1_mpt_prove_same_plaintext_multi(
        const secp256k1_context* ctx,
        unsigned char* proof_out,
        size_t* proof_len,
        uint64_t amount_m,
        size_t n_ciphertexts,
        const secp256k1_pubkey* R_array,
        const secp256k1_pubkey* S_array,
        const secp256k1_pubkey* Pk_array,
        const unsigned char* r_array,
        const unsigned char* tx_context_id
    );

    int secp256k1_mpt_verify_same_plaintext_multi(
        const secp256k1_context* ctx,
        const unsigned char* proof,
        size_t proof_len,
        size_t n_ciphertexts,
        const secp256k1_pubkey* R_array,
        const secp256k1_pubkey* S_array,
        const secp256k1_pubkey* Pk_array,
        const unsigned char* tx_context_id
    );

    // Constants
    #define SECP256K1_CONTEXT_SIGN ...
    #define SECP256K1_CONTEXT_VERIFY ...
    #define SECP256K1_EC_COMPRESSED ...
    #define SECP256K1_EC_UNCOMPRESSED ...
"""
)

# Set the source code to compile
script_dir = os.path.dirname(os.path.abspath(__file__))

# Determine platform-specific library directory
system = platform.system().lower()
if system == "darwin":
    lib_subdir = "darwin"
elif system == "linux":
    lib_subdir = "linux"
elif system == "windows" or system.startswith("win"):
    lib_subdir = "win32"
else:
    raise RuntimeError(f"Unsupported platform: {system}")

# Use pre-compiled libraries from the libs directory
libs_dir = os.path.join(script_dir, "libs", lib_subdir)
include_dir = os.path.join(script_dir, "include")

# Check if libraries exist
if not os.path.exists(libs_dir):
    raise RuntimeError(
        f"Pre-compiled libraries not found for platform '{lib_subdir}'. "
        f"Expected directory: {libs_dir}\n"
        f"Please ensure the pre-compiled libraries are included in the repository."
    )

# Platform-specific library and include directories
library_dirs = [libs_dir]
include_dirs = [include_dir]

# On macOS, add Homebrew OpenSSL paths
if system == "darwin":
    # Try common Homebrew OpenSSL locations
    homebrew_openssl_paths = [
        "/opt/homebrew/opt/openssl/lib",  # Apple Silicon
        "/usr/local/opt/openssl/lib",  # Intel
        "/opt/homebrew/opt/openssl@3/lib",  # Apple Silicon OpenSSL 3
        "/usr/local/opt/openssl@3/lib",  # Intel OpenSSL 3
    ]
    homebrew_openssl_include_paths = [
        "/opt/homebrew/opt/openssl/include",
        "/usr/local/opt/openssl/include",
        "/opt/homebrew/opt/openssl@3/include",
        "/usr/local/opt/openssl@3/include",
    ]

    for path in homebrew_openssl_paths:
        if os.path.exists(path):
            library_dirs.append(path)
            break

    for path in homebrew_openssl_include_paths:
        if os.path.exists(path):
            include_dirs.append(path)
            break

ffibuilder.set_source(
    "_mpt_crypto",
    """
    #include <secp256k1.h>
    #include <secp256k1_mpt.h>
    """,
    libraries=["mpt-crypto", "secp256k1", "crypto"],
    library_dirs=library_dirs,
    include_dirs=include_dirs,
)

if __name__ == "__main__":
    ffibuilder.compile(verbose=True)
