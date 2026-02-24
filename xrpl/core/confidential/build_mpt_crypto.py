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

    // Bulletproof (Range Proof) - Aggregated API
    int secp256k1_bulletproof_create_commitment(
        const secp256k1_context* ctx,
        secp256k1_pubkey* commitment_C,
        uint64_t value,
        const unsigned char* blinding_factor,
        const secp256k1_pubkey* pk_base
    );

    int secp256k1_bulletproof_prove_agg(
        const secp256k1_context* ctx,
        unsigned char* proof_out,
        size_t* proof_len,
        const uint64_t* values,
        const unsigned char* blindings_flat,
        size_t m,
        const secp256k1_pubkey* pk_base,
        const unsigned char* context_id
    );

    int secp256k1_bulletproof_verify_agg(
        const secp256k1_context* ctx,
        const secp256k1_pubkey* G_vec,
        const secp256k1_pubkey* H_vec,
        const unsigned char* proof,
        size_t proof_len,
        const secp256k1_pubkey* commitment_C_vec,
        size_t m,
        const secp256k1_pubkey* pk_base,
        const unsigned char* context_id
    );

    // Generator helpers
    int secp256k1_mpt_get_h_generator(
        const secp256k1_context* ctx,
        secp256k1_pubkey* h
    );

    int secp256k1_mpt_get_generator_vector(
        const secp256k1_context* ctx,
        secp256k1_pubkey* vec,
        size_t n,
        const unsigned char* label,
        size_t label_len
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

    // ========================================================================
    // MPT Utility Layer - High-level wrapper functions
    // ========================================================================

    // Structs
    typedef struct {
        uint8_t bytes[24];
    } mpt_issuance_id;

    typedef struct {
        uint8_t bytes[20];
    } account_id;

    struct mpt_confidential_recipient {
        uint8_t pubkey[33];
        uint8_t encrypted_amount[66];
    };

    struct mpt_pedersen_proof_params {
        uint8_t pedersen_commitment[33];
        uint64_t amount;
        uint8_t encrypted_amount[66];
        uint8_t blinding_factor[32];
    };

    // Context functions
    secp256k1_context* mpt_secp256k1_context();

    // Context hash functions
    int mpt_get_convert_context_hash(
        account_id account,
        uint32_t sequence,
        mpt_issuance_id issuanceID,
        uint64_t amount,
        uint8_t out_hash[32]
    );

    int mpt_get_convert_back_context_hash(
        account_id account,
        uint32_t sequence,
        mpt_issuance_id issuanceID,
        uint64_t amount,
        uint32_t version,
        uint8_t out_hash[32]
    );

    int mpt_get_send_context_hash(
        account_id account,
        uint32_t sequence,
        mpt_issuance_id issuanceID,
        account_id destination,
        uint32_t version,
        uint8_t out_hash[32]
    );

    int mpt_get_clawback_context_hash(
        account_id account,
        uint32_t sequence,
        mpt_issuance_id issuanceID,
        uint64_t amount,
        account_id holder,
        uint8_t out_hash[32]
    );

    // Size calculation functions
    size_t get_multi_ciphertext_equality_proof_size(size_t n_recipients);
    size_t get_confidential_send_proof_size(size_t n_recipients);

    // Key & Ciphertext Utilities
    int mpt_generate_keypair(uint8_t* out_privkey, uint8_t* out_pubkey);
    int mpt_generate_blinding_factor(uint8_t out_factor[32]);

    int mpt_encrypt_amount(
        uint64_t amount,
        uint8_t const pubkey[33],
        uint8_t const blinding_factor[32],
        uint8_t out_ciphertext[66]
    );

    int mpt_decrypt_amount(
        uint8_t const ciphertext[66],
        uint8_t const privkey[32],
        uint64_t* out_amount
    );

    // Proof Generation
    int mpt_get_convert_proof(
        uint8_t const pubkey[33],
        uint8_t const privkey[32],
        uint8_t const ctx_hash[32],
        uint8_t out_proof[65]
    );

    int mpt_get_pedersen_commitment(
        uint64_t amount,
        uint8_t const blinding_factor[32],
        uint8_t out_commitment[33]
    );

    int mpt_get_amount_linkage_proof(
        uint8_t const pubkey[33],
        uint8_t const blinding_factor[32],
        uint8_t const context_hash[32],
        struct mpt_pedersen_proof_params const* params,
        uint8_t out[195]
    );

    int mpt_get_balance_linkage_proof(
        uint8_t const priv[32],
        uint8_t const pub[33],
        uint8_t const context_hash[32],
        struct mpt_pedersen_proof_params const* params,
        uint8_t out[195]
    );

    int mpt_get_confidential_send_proof(
        uint8_t const priv[32],
        uint64_t amount,
        struct mpt_confidential_recipient const* recipients,
        size_t n_recipients,
        uint8_t const tx_blinding_factor[32],
        uint8_t const context_hash[32],
        struct mpt_pedersen_proof_params const* amount_params,
        struct mpt_pedersen_proof_params const* balance_params,
        uint8_t* out_proof,
        size_t* out_len
    );

    int mpt_get_convert_back_proof(
        uint8_t const priv[32],
        uint8_t const pub[33],
        uint8_t const context_hash[32],
        struct mpt_pedersen_proof_params const* params,
        uint8_t out_proof[195]
    );

    int mpt_get_clawback_proof(
        uint8_t const priv[32],
        uint8_t const pub[33],
        uint8_t const context_hash[32],
        uint64_t const amount,
        uint8_t const encrypted_amount[66],
        uint8_t out_proof[98]
    );
"""
)

script_dir = os.path.dirname(os.path.abspath(__file__))
system = platform.system().lower()

if system == "darwin":
    lib_subdir = "darwin"
elif system == "linux":
    lib_subdir = "linux"
elif system == "windows" or system.startswith("win"):
    lib_subdir = "win32"
else:
    raise RuntimeError(f"Unsupported platform: {system}")

libs_dir = os.path.join(script_dir, "libs", lib_subdir)
include_dir = os.path.join(script_dir, "include")

if not os.path.exists(libs_dir):
    raise RuntimeError(
        f"Pre-compiled libraries not found for platform '{lib_subdir}'. "
        f"Expected directory: {libs_dir}"
    )

library_dirs = [libs_dir]
include_dirs = [include_dir]

if system == "darwin":
    homebrew_openssl_paths = [
        "/opt/homebrew/opt/openssl/lib",
        "/usr/local/opt/openssl/lib",
        "/opt/homebrew/opt/openssl@3/lib",
        "/usr/local/opt/openssl@3/lib",
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

extra_compile_args = []
extra_link_args = []
libraries = ["mpt-crypto", "secp256k1", "crypto"]

if system == "darwin":
    # macOS: Link C++ standard library and use -all_load to include all symbols
    libraries.append("c++")
    extra_link_args = ["-Wl,-all_load"]
elif system == "linux":
    # Linux: Link C++ standard library and use PIC for shared library
    libraries.append("stdc++")
    extra_compile_args = ["-fPIC"]
elif system == "windows" or system.startswith("win"):
    libraries.extend(["zlib", "Advapi32", "User32", "Crypt32", "Ws2_32"])
    extra_link_args = [
        "/WHOLEARCHIVE:mpt-crypto.lib",
        "/WHOLEARCHIVE:secp256k1.lib",
    ]

ffibuilder.set_source(
    "_mpt_crypto",
    """
    #include <secp256k1.h>
    #include <secp256k1_mpt.h>

    // Forward declare utility layer functions (avoid including C++ header)
    #ifdef __cplusplus
    extern "C" {
    #endif

    // Include only the C-compatible parts of the utility layer
    #include <stdint.h>
    #include <stddef.h>

    typedef struct {
        uint8_t bytes[24];
    } mpt_issuance_id;

    typedef struct {
        uint8_t bytes[20];
    } account_id;

    struct mpt_confidential_recipient {
        uint8_t pubkey[33];
        uint8_t encrypted_amount[66];
    };

    struct mpt_pedersen_proof_params {
        uint8_t pedersen_commitment[33];
        uint64_t amount;
        uint8_t encrypted_amount[66];
        uint8_t blinding_factor[32];
    };

    // Declare utility layer functions
    secp256k1_context* mpt_secp256k1_context(void);

    int mpt_get_convert_context_hash(
        account_id account,
        uint32_t sequence,
        mpt_issuance_id issuanceID,
        uint64_t amount,
        uint8_t out_hash[32]
    );

    int mpt_get_convert_back_context_hash(
        account_id account,
        uint32_t sequence,
        mpt_issuance_id issuanceID,
        uint64_t amount,
        uint32_t version,
        uint8_t out_hash[32]
    );

    int mpt_get_send_context_hash(
        account_id account,
        uint32_t sequence,
        mpt_issuance_id issuanceID,
        account_id destination,
        uint32_t version,
        uint8_t out_hash[32]
    );

    int mpt_get_clawback_context_hash(
        account_id account,
        uint32_t sequence,
        mpt_issuance_id issuanceID,
        uint64_t amount,
        account_id holder,
        uint8_t out_hash[32]
    );

    size_t get_multi_ciphertext_equality_proof_size(size_t n_recipients);
    size_t get_confidential_send_proof_size(size_t n_recipients);

    int mpt_generate_keypair(uint8_t* out_privkey, uint8_t* out_pubkey);
    int mpt_generate_blinding_factor(uint8_t out_factor[32]);

    int mpt_encrypt_amount(
        uint64_t amount,
        uint8_t const pubkey[33],
        uint8_t const blinding_factor[32],
        uint8_t out_ciphertext[66]
    );

    int mpt_decrypt_amount(
        uint8_t const ciphertext[66],
        uint8_t const privkey[32],
        uint64_t* out_amount
    );

    int mpt_get_convert_proof(
        uint8_t const pubkey[33],
        uint8_t const privkey[32],
        uint8_t const ctx_hash[32],
        uint8_t out_proof[65]
    );

    int mpt_get_pedersen_commitment(
        uint64_t amount,
        uint8_t const blinding_factor[32],
        uint8_t out_commitment[33]
    );

    int mpt_get_amount_linkage_proof(
        uint8_t const pubkey[33],
        uint8_t const blinding_factor[32],
        uint8_t const context_hash[32],
        struct mpt_pedersen_proof_params const* params,
        uint8_t out[195]
    );

    int mpt_get_balance_linkage_proof(
        uint8_t const priv[32],
        uint8_t const pub[33],
        uint8_t const context_hash[32],
        struct mpt_pedersen_proof_params const* params,
        uint8_t out[195]
    );

    int mpt_get_confidential_send_proof(
        uint8_t const priv[32],
        uint64_t amount,
        struct mpt_confidential_recipient const* recipients,
        size_t n_recipients,
        uint8_t const tx_blinding_factor[32],
        uint8_t const context_hash[32],
        struct mpt_pedersen_proof_params const* amount_params,
        struct mpt_pedersen_proof_params const* balance_params,
        uint8_t* out_proof,
        size_t* out_len
    );

    int mpt_get_convert_back_proof(
        uint8_t const priv[32],
        uint8_t const pub[33],
        uint8_t const context_hash[32],
        struct mpt_pedersen_proof_params const* params,
        uint8_t out_proof[195]
    );

    int mpt_get_clawback_proof(
        uint8_t const priv[32],
        uint8_t const pub[33],
        uint8_t const context_hash[32],
        uint64_t const amount,
        uint8_t const encrypted_amount[66],
        uint8_t out_proof[98]
    );

    #ifdef __cplusplus
    }
    #endif
    """,
    libraries=libraries,
    library_dirs=library_dirs,
    include_dirs=include_dirs,
    extra_compile_args=extra_compile_args,
    extra_link_args=extra_link_args,
)

if __name__ == "__main__":
    # Change to the script directory to avoid setuptools package discovery issues
    original_dir = os.getcwd()
    os.chdir(script_dir)
    try:
        ffibuilder.compile(verbose=True)

        # Clean up generated C source file (intermediate build artifact)
        c_file = os.path.join(script_dir, "_mpt_crypto.c")
        if os.path.exists(c_file):
            os.remove(c_file)
            print(f"Cleaned up intermediate file: {c_file}")
    finally:
        os.chdir(original_dir)
