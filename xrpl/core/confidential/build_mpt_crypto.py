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

    int secp256k1_elgamal_verify_encryption(
        const secp256k1_context* ctx,
        const secp256k1_pubkey* c1,
        const secp256k1_pubkey* c2,
        const secp256k1_pubkey* pubkey_Q,
        uint64_t amount,
        const unsigned char* blinding_factor
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

    // Scalar arithmetic helpers
    void secp256k1_mpt_scalar_add(unsigned char *res, const unsigned char *a, const unsigned char *b);
    void secp256k1_mpt_scalar_negate(unsigned char *res, const unsigned char *in);

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

    // Equality proof with shared randomness
    size_t secp256k1_mpt_proof_equality_shared_r_size(size_t n);

    int secp256k1_mpt_prove_equality_shared_r(
        const secp256k1_context* ctx,
        unsigned char* proof_out,
        uint64_t amount,
        const unsigned char* r_shared,
        size_t n,
        const secp256k1_pubkey* C1,
        const secp256k1_pubkey* C2_vec,
        const secp256k1_pubkey* Pk_vec,
        const unsigned char* context_id
    );

    int secp256k1_mpt_verify_equality_shared_r(
        const secp256k1_context* ctx,
        const unsigned char* proof,
        size_t n,
        const secp256k1_pubkey* C1,
        const secp256k1_pubkey* C2_vec,
        const secp256k1_pubkey* Pk_vec,
        const unsigned char* context_id
    );

    // Compact standard send proof
    int secp256k1_compact_standard_prove(
        const secp256k1_context* ctx,
        unsigned char* proof_out,
        uint64_t amount,
        uint64_t balance,
        const unsigned char* r_shared,
        const unsigned char* sk_A,
        const unsigned char* r_b,
        size_t n,
        const secp256k1_pubkey* C1,
        const secp256k1_pubkey* C2_vec,
        const secp256k1_pubkey* Pk_vec,
        const secp256k1_pubkey* PC_m,
        const secp256k1_pubkey* pk_A,
        const secp256k1_pubkey* PC_b,
        const secp256k1_pubkey* B1,
        const secp256k1_pubkey* B2,
        const unsigned char* context_id
    );

    int secp256k1_compact_standard_verify(
        const secp256k1_context* ctx,
        const unsigned char* proof,
        size_t n,
        const secp256k1_pubkey* C1,
        const secp256k1_pubkey* C2_vec,
        const secp256k1_pubkey* Pk_vec,
        const secp256k1_pubkey* PC_m,
        const secp256k1_pubkey* pk_A,
        const secp256k1_pubkey* PC_b,
        const secp256k1_pubkey* B1,
        const secp256k1_pubkey* B2,
        const unsigned char* context_id
    );

    // Compact clawback proof
    int secp256k1_compact_clawback_prove(
        const secp256k1_context* ctx,
        unsigned char* proof_out,
        uint64_t amount,
        const unsigned char* sk_iss,
        const secp256k1_pubkey* P_iss,
        const secp256k1_pubkey* C1,
        const secp256k1_pubkey* C2,
        const unsigned char* context_id
    );

    int secp256k1_compact_clawback_verify(
        const secp256k1_context* ctx,
        const unsigned char* proof,
        uint64_t amount,
        const secp256k1_pubkey* P_iss,
        const secp256k1_pubkey* C1,
        const secp256k1_pubkey* C2,
        const unsigned char* context_id
    );

    // Compact convertback proof
    int secp256k1_compact_convertback_prove(
        const secp256k1_context* ctx,
        unsigned char* proof_out,
        uint64_t balance,
        const unsigned char* sk_A,
        const unsigned char* rho,
        const secp256k1_pubkey* pk_A,
        const secp256k1_pubkey* B1,
        const secp256k1_pubkey* B2,
        const secp256k1_pubkey* PC_b,
        const unsigned char* context_id
    );

    int secp256k1_compact_convertback_verify(
        const secp256k1_context* ctx,
        const unsigned char* proof,
        const secp256k1_pubkey* pk_A,
        const secp256k1_pubkey* B1,
        const secp256k1_pubkey* B2,
        const secp256k1_pubkey* PC_b,
        const unsigned char* context_id
    );

    // Constants
    #define SECP256K1_CONTEXT_SIGN ...
    #define SECP256K1_CONTEXT_VERIFY ...
    #define SECP256K1_EC_COMPRESSED ...
    #define SECP256K1_EC_UNCOMPRESSED ...

    // ========================================================================
    // MPT Utility Layer - High-level wrapper functions
    // (must match XRPLF/mpt-crypto include/utility/mpt_utility.h)
    // ========================================================================

    // Structs
    typedef struct {
        uint8_t bytes[24];
    } mpt_issuance_id;

    typedef struct {
        uint8_t bytes[20];
    } account_id;

    typedef struct mpt_confidential_participant {
        uint8_t pubkey[33];
        uint8_t ciphertext[66];
    } mpt_confidential_participant;

    typedef struct mpt_pedersen_proof_params {
        uint8_t pedersen_commitment[33];
        uint64_t amount;
        uint8_t ciphertext[66];
        uint8_t blinding_factor[32];
    } mpt_pedersen_proof_params;

    // Context functions
    secp256k1_context* mpt_secp256k1_context();

    // Context hash functions
    int mpt_get_convert_context_hash(
        account_id account,
        mpt_issuance_id iss,
        uint32_t sequence,
        uint8_t out_hash[32]
    );

    int mpt_get_convert_back_context_hash(
        account_id acc,
        mpt_issuance_id iss,
        uint32_t seq,
        uint32_t ver,
        uint8_t out_hash[32]
    );

    int mpt_get_send_context_hash(
        account_id acc,
        mpt_issuance_id iss,
        uint32_t seq,
        account_id dest,
        uint32_t ver,
        uint8_t out_hash[32]
    );

    int mpt_get_clawback_context_hash(
        account_id acc,
        mpt_issuance_id iss,
        uint32_t seq,
        account_id holder,
        uint8_t out_hash[32]
    );

    // Size calculation functions
    size_t get_confidential_send_proof_size(size_t n_recipients);

    // Key & Ciphertext Utilities
    int mpt_make_ec_pair(
        uint8_t const buffer[66],
        secp256k1_pubkey* out1,
        secp256k1_pubkey* out2
    );

    int mpt_serialize_ec_pair(
        secp256k1_pubkey const* in1,
        secp256k1_pubkey const* in2,
        uint8_t out[66]
    );

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
        uint8_t out_proof[64]
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
        mpt_pedersen_proof_params const* params,
        uint8_t out[195]
    );

    int mpt_get_balance_linkage_proof(
        uint8_t const priv[32],
        uint8_t const pub[33],
        uint8_t const context_hash[32],
        mpt_pedersen_proof_params const* params,
        uint8_t out[195]
    );

    int mpt_get_confidential_send_proof(
        uint8_t const priv[32],
        uint64_t amount,
        mpt_confidential_participant const* recipients,
        size_t n_recipients,
        uint8_t const tx_blinding_factor[32],
        uint8_t const context_hash[32],
        mpt_pedersen_proof_params const* amount_params,
        mpt_pedersen_proof_params const* balance_params,
        uint8_t* out_proof,
        size_t* out_len
    );

    int mpt_get_convert_back_proof(
        uint8_t const priv[32],
        uint8_t const pub[33],
        uint8_t const context_hash[32],
        uint64_t const amount,
        mpt_pedersen_proof_params const* params,
        uint8_t out_proof[883]
    );

    int mpt_get_clawback_proof(
        uint8_t const priv[32],
        uint8_t const pub[33],
        uint8_t const context_hash[32],
        uint64_t const amount,
        uint8_t const ciphertext[66],
        uint8_t out_proof[98]
    );

    // Encryption & Commitment Validation
    int mpt_verify_revealed_amount(
        uint64_t const amount,
        uint8_t const blinding_factor[32],
        mpt_confidential_participant const* holder,
        mpt_confidential_participant const* issuer,
        mpt_confidential_participant const* auditor
    );

    // ZKProof Verifications
    int mpt_verify_convert_proof(
        uint8_t const proof[64],
        uint8_t const pubkey[33],
        uint8_t const context_hash[32]
    );

    int mpt_verify_convert_back_proof(
        uint8_t const proof[883],
        uint8_t const pubkey[33],
        uint8_t const ciphertext[66],
        uint8_t const balance_commitment[33],
        uint64_t const amount,
        uint8_t const context_hash[32]
    );

    int mpt_verify_send_proof(
        uint8_t const* proof,
        size_t const proof_len,
        mpt_confidential_participant const* participants,
        uint8_t const n_participants,
        uint8_t const sender_spending_ciphertext[66],
        uint8_t const amount_commitment[33],
        uint8_t const balance_commitment[33],
        uint8_t const context_hash[32]
    );

    int mpt_verify_clawback_proof(
        uint8_t const proof[98],
        uint64_t const amount,
        uint8_t const pubkey[33],
        uint8_t const ciphertext[66],
        uint8_t const context_hash[32]
    );

    // Internal verification components
    int mpt_verify_amount_linkage(
        secp256k1_context const* ctx,
        uint8_t const proof[195],
        uint8_t const ciphertext[66],
        uint8_t const pubkey[33],
        uint8_t const commitment[33],
        uint8_t const context_hash[32]
    );

    int mpt_verify_balance_linkage(
        uint8_t const proof[195],
        uint8_t const ciphertext[66],
        uint8_t const pubkey[33],
        uint8_t const commitment[33],
        uint8_t const context_hash[32]
    );

    int mpt_verify_equality_proof(
        secp256k1_context const* ctx,
        uint8_t const* proof,
        size_t const proof_len,
        mpt_confidential_participant const* participants,
        uint8_t const n_participants,
        uint8_t const context_hash[32]
    );

    int mpt_compute_convert_back_remainder(
        uint8_t const commitment_in[33],
        uint64_t amount,
        uint8_t commitment_out[33]
    );

    int mpt_verify_aggregated_bulletproof(
        uint8_t const* proof,
        size_t proof_len,
        uint8_t const** compressed_commitments,
        size_t m,
        uint8_t const context_hash[32]
    );

    int mpt_verify_send_range_proof(
        secp256k1_context const* ctx,
        uint8_t const proof[754],
        uint8_t const amount_commitment[33],
        uint8_t const remainder_commitment[33],
        uint8_t const context_hash[32]
    );
"""
)

# ──────────────────────────────────────────────────────────────────────────────
# Locate the pre-built shared library
#
# The CI now builds mpt-crypto as a single self-contained shared library with
# secp256k1 and OpenSSL statically linked in.  This is much smaller than the
# old approach of shipping three separate static archives (.a / .lib).
#
# Expected layout:
#   libs/linux/libmpt-crypto.so
#   libs/darwin/libmpt-crypto.dylib
#   libs/win32/mpt-crypto.dll
# ──────────────────────────────────────────────────────────────────────────────
script_dir = os.path.dirname(os.path.abspath(__file__))
system = platform.system().lower()

if system == "darwin":
    lib_subdir = "darwin"
    shared_lib_name = "libmpt-crypto.dylib"
elif system == "linux":
    lib_subdir = "linux"
    shared_lib_name = "libmpt-crypto.so"
elif system == "windows" or system.startswith("win"):
    lib_subdir = "win32"
    shared_lib_name = "mpt-crypto.dll"
else:
    raise RuntimeError(f"Unsupported platform: {system}")

libs_dir = os.path.join(script_dir, "libs", lib_subdir)
include_dir = os.path.join(script_dir, "include")

if not os.path.exists(libs_dir):
    raise RuntimeError(
        f"Pre-compiled libraries not found for platform '{lib_subdir}'. "
        f"Expected directory: {libs_dir}"
    )

shared_lib_path = os.path.join(libs_dir, shared_lib_name)
if not os.path.exists(shared_lib_path):
    raise RuntimeError(
        f"Shared library not found: {shared_lib_path}\n"
        f"Contents of {libs_dir}: {os.listdir(libs_dir)}\n"
        f"\n"
        f"The CI now builds mpt-crypto as a shared library (.so/.dylib/.dll)\n"
        f"instead of separate static archives (.a/.lib).\n"
        f"Run: ./xrpl/core/confidential/setup_mpt_crypto.sh download"
    )

library_dirs = [libs_dir]
include_dirs = [include_dir]

extra_compile_args = []
extra_link_args = []

# Link against the single shared library — all dependencies (secp256k1,
# OpenSSL) are already statically linked inside it.
libraries = ["mpt-crypto"]

if system == "darwin":
    # Set rpath so the extension can find the shared library at runtime
    extra_link_args = [
        f"-Wl,-rpath,{libs_dir}",
        f"-Wl,-rpath,@loader_path/libs/{lib_subdir}",
    ]
elif system == "linux":
    extra_compile_args = ["-fPIC"]
    extra_link_args = [
        f"-Wl,-rpath,{libs_dir}",
        f"-Wl,-rpath,$ORIGIN/libs/{lib_subdir}",
    ]
elif system == "windows" or system.startswith("win"):
    # On Windows the DLL just needs to be on PATH or in the same directory
    libraries = ["mpt-crypto"]

ffibuilder.set_source(
    "_mpt_crypto",
    """
    #include <stdbool.h>
    #include <stdint.h>
    #include <stddef.h>

    #include <secp256k1.h>
    #include <secp256k1_mpt.h>

    // Forward declare utility layer functions (avoid including C++ header)
    #ifdef __cplusplus
    extern "C" {
    #endif

    typedef struct {
        uint8_t bytes[24];
    } mpt_issuance_id;

    typedef struct {
        uint8_t bytes[20];
    } account_id;

    typedef struct mpt_confidential_participant {
        uint8_t pubkey[33];
        uint8_t ciphertext[66];
    } mpt_confidential_participant;

    typedef struct mpt_pedersen_proof_params {
        uint8_t pedersen_commitment[33];
        uint64_t amount;
        uint8_t ciphertext[66];
        uint8_t blinding_factor[32];
    } mpt_pedersen_proof_params;

    // Declare utility layer functions
    secp256k1_context* mpt_secp256k1_context(void);

    int mpt_get_convert_context_hash(
        account_id account,
        mpt_issuance_id iss,
        uint32_t sequence,
        uint8_t out_hash[32]
    );

    int mpt_get_convert_back_context_hash(
        account_id acc,
        mpt_issuance_id iss,
        uint32_t seq,
        uint32_t ver,
        uint8_t out_hash[32]
    );

    int mpt_get_send_context_hash(
        account_id acc,
        mpt_issuance_id iss,
        uint32_t seq,
        account_id dest,
        uint32_t ver,
        uint8_t out_hash[32]
    );

    int mpt_get_clawback_context_hash(
        account_id acc,
        mpt_issuance_id iss,
        uint32_t seq,
        account_id holder,
        uint8_t out_hash[32]
    );

    size_t get_confidential_send_proof_size(size_t n_recipients);

    int mpt_make_ec_pair(
        uint8_t const buffer[66],
        secp256k1_pubkey* out1,
        secp256k1_pubkey* out2
    );

    int mpt_serialize_ec_pair(
        secp256k1_pubkey const* in1,
        secp256k1_pubkey const* in2,
        uint8_t out[66]
    );

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
        uint8_t out_proof[64]
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
        mpt_pedersen_proof_params const* params,
        uint8_t out[195]
    );

    int mpt_get_balance_linkage_proof(
        uint8_t const priv[32],
        uint8_t const pub[33],
        uint8_t const context_hash[32],
        mpt_pedersen_proof_params const* params,
        uint8_t out[195]
    );

    int mpt_get_confidential_send_proof(
        uint8_t const priv[32],
        uint64_t amount,
        mpt_confidential_participant const* recipients,
        size_t n_recipients,
        uint8_t const tx_blinding_factor[32],
        uint8_t const context_hash[32],
        mpt_pedersen_proof_params const* amount_params,
        mpt_pedersen_proof_params const* balance_params,
        uint8_t* out_proof,
        size_t* out_len
    );

    int mpt_get_convert_back_proof(
        uint8_t const priv[32],
        uint8_t const pub[33],
        uint8_t const context_hash[32],
        uint64_t const amount,
        mpt_pedersen_proof_params const* params,
        uint8_t out_proof[883]
    );

    int mpt_get_clawback_proof(
        uint8_t const priv[32],
        uint8_t const pub[33],
        uint8_t const context_hash[32],
        uint64_t const amount,
        uint8_t const ciphertext[66],
        uint8_t out_proof[98]
    );

    int mpt_verify_revealed_amount(
        uint64_t const amount,
        uint8_t const blinding_factor[32],
        mpt_confidential_participant const* holder,
        mpt_confidential_participant const* issuer,
        mpt_confidential_participant const* auditor
    );

    int mpt_verify_convert_proof(
        uint8_t const proof[64],
        uint8_t const pubkey[33],
        uint8_t const context_hash[32]
    );

    int mpt_verify_convert_back_proof(
        uint8_t const proof[883],
        uint8_t const pubkey[33],
        uint8_t const ciphertext[66],
        uint8_t const balance_commitment[33],
        uint64_t const amount,
        uint8_t const context_hash[32]
    );

    int mpt_verify_send_proof(
        uint8_t const* proof,
        size_t const proof_len,
        mpt_confidential_participant const* participants,
        uint8_t const n_participants,
        uint8_t const sender_spending_ciphertext[66],
        uint8_t const amount_commitment[33],
        uint8_t const balance_commitment[33],
        uint8_t const context_hash[32]
    );

    int mpt_verify_clawback_proof(
        uint8_t const proof[98],
        uint64_t const amount,
        uint8_t const pubkey[33],
        uint8_t const ciphertext[66],
        uint8_t const context_hash[32]
    );

    int mpt_verify_amount_linkage(
        secp256k1_context const* ctx,
        uint8_t const proof[195],
        uint8_t const ciphertext[66],
        uint8_t const pubkey[33],
        uint8_t const commitment[33],
        uint8_t const context_hash[32]
    );

    int mpt_verify_balance_linkage(
        uint8_t const proof[195],
        uint8_t const ciphertext[66],
        uint8_t const pubkey[33],
        uint8_t const commitment[33],
        uint8_t const context_hash[32]
    );

    int mpt_verify_equality_proof(
        secp256k1_context const* ctx,
        uint8_t const* proof,
        size_t const proof_len,
        mpt_confidential_participant const* participants,
        uint8_t const n_participants,
        uint8_t const context_hash[32]
    );

    int mpt_compute_convert_back_remainder(
        uint8_t const commitment_in[33],
        uint64_t amount,
        uint8_t commitment_out[33]
    );

    int mpt_verify_aggregated_bulletproof(
        uint8_t const* proof,
        size_t proof_len,
        uint8_t const** compressed_commitments,
        size_t m,
        uint8_t const context_hash[32]
    );

    int mpt_verify_send_range_proof(
        secp256k1_context const* ctx,
        uint8_t const proof[754],
        uint8_t const amount_commitment[33],
        uint8_t const remainder_commitment[33],
        uint8_t const context_hash[32]
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

        # Print summary
        print("")
        print("Build complete!")
        print(f"  Shared library: {shared_lib_path}")
        print(f"  Size: {os.path.getsize(shared_lib_path) / (1024*1024):.1f} MB")
    finally:
        os.chdir(original_dir)
