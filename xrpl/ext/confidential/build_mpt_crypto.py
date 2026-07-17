"""
Build script for mpt-crypto C library Python bindings using cffi.
"""

import os
import platform
import sys

from cffi import FFI

ffibuilder = FFI()

# Define the C API that we want to expose to Python
ffibuilder.cdef(
    """
    // ────────────────────────────────────────────────────────────────────
    // Prover-focused FFI surface for mpt-crypto (XLS-0096 Confidential MPT).
    //
    // Signatures here are validated AGAINST the real headers at build time:
    // set_source() #includes utility/mpt_utility.h + secp256k1_mpt.h, so the C
    // compiler errors if any declaration below drifts from the library ABI.
    // Pinned to mpt-crypto MPT_CRYPTO_VERSION (see that file).
    // ────────────────────────────────────────────────────────────────────

    // ---- secp256k1 opaque types ----
    typedef struct secp256k1_context_struct secp256k1_context;
    typedef struct { unsigned char data[64]; } secp256k1_pubkey;

    secp256k1_context* secp256k1_context_create(unsigned int flags);
    void secp256k1_context_destroy(secp256k1_context* ctx);
    int secp256k1_ec_pubkey_parse(
        const secp256k1_context* ctx,
        secp256k1_pubkey* pubkey,
        const unsigned char* input,
        size_t inputlen
    );

    // ---- Bulletproof range proofs (aggregated API) ----
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
    int secp256k1_mpt_get_generator_vector(
        const secp256k1_context* ctx,
        secp256k1_pubkey* vec,
        size_t n,
        const unsigned char* label,
        size_t label_len
    );

    // ---- MPT utility-layer structs (mirror utility/mpt_utility.h) ----
    typedef struct { uint8_t bytes[24]; } mpt_issuance_id;
    typedef struct { uint8_t bytes[20]; } account_id;
    typedef struct {
        uint8_t pubkey[33];
        uint8_t ciphertext[66];
    } mpt_confidential_participant;
    typedef struct {
        uint8_t pedersen_commitment[33];
        uint64_t amount;
        uint8_t ciphertext[66];
        uint8_t blinding_factor[32];
    } mpt_pedersen_proof_params;

    // ---- Context hashes ----
    int mpt_get_convert_context_hash(
        account_id account, mpt_issuance_id iss, uint32_t sequence,
        uint8_t out_hash[32]
    );
    int mpt_get_convert_back_context_hash(
        account_id acc, mpt_issuance_id iss, uint32_t seq, uint32_t ver,
        uint8_t out_hash[32]
    );
    int mpt_get_send_context_hash(
        account_id acc, mpt_issuance_id iss, uint32_t seq, account_id dest,
        uint32_t ver, uint8_t out_hash[32]
    );
    int mpt_get_clawback_context_hash(
        account_id acc, mpt_issuance_id iss, uint32_t seq, account_id holder,
        uint8_t out_hash[32]
    );

    // ---- Keys / encryption / commitment ----
    int mpt_generate_keypair(uint8_t* out_privkey, uint8_t* out_pubkey);
    int mpt_generate_blinding_factor(uint8_t out_factor[32]);
    int mpt_encrypt_amount(
        uint64_t amount,
        const uint8_t pubkey[33],
        const uint8_t blinding_factor[32],
        uint8_t out_ciphertext[66]
    );
    int mpt_decrypt_amount(
        const uint8_t ciphertext[66],
        const uint8_t privkey[32],
        uint64_t* out_amount,
        uint64_t range_low,
        uint64_t range_high
    );
    int mpt_get_pedersen_commitment(
        uint64_t amount,
        const uint8_t blinding_factor[32],
        uint8_t out_commitment[33]
    );

    // ---- Proof generation + verification ----
    int mpt_get_convert_proof(
        const uint8_t pubkey[33], const uint8_t privkey[32],
        const uint8_t ctx_hash[32], uint8_t out_proof[64]
    );
    int mpt_verify_convert_proof(
        const uint8_t proof[64], const uint8_t pubkey[33],
        const uint8_t context_hash[32]
    );
    int mpt_get_confidential_send_proof(
        const uint8_t priv[32], const uint8_t pub[33], uint64_t amount,
        const mpt_confidential_participant* participants, size_t n_participants,
        const uint8_t tx_blinding_factor[32], const uint8_t context_hash[32],
        const uint8_t amount_commitment[33],
        const mpt_pedersen_proof_params* balance_params,
        uint8_t* out_proof, size_t* out_len
    );
    int mpt_verify_send_proof(
        const uint8_t* proof,
        const mpt_confidential_participant* participants,
        uint8_t n_participants,
        const uint8_t sender_spending_ciphertext[66],
        const uint8_t amount_commitment[33],
        const uint8_t balance_commitment[33],
        const uint8_t context_hash[32]
    );
    int mpt_get_convert_back_proof(
        const uint8_t priv[32], const uint8_t pub[33],
        const uint8_t context_hash[32], uint64_t amount,
        const mpt_pedersen_proof_params* params, uint8_t* out_proof
    );
    int mpt_verify_convert_back_proof(
        const uint8_t* proof, const uint8_t pubkey[33],
        const uint8_t ciphertext[66], const uint8_t balance_commitment[33],
        uint64_t amount, const uint8_t context_hash[32]
    );
    int mpt_get_clawback_proof(
        const uint8_t priv[32], const uint8_t pub[33],
        const uint8_t context_hash[32], uint64_t amount,
        const uint8_t ciphertext[66], uint8_t* out_proof
    );
    int mpt_verify_clawback_proof(
        const uint8_t* proof, uint64_t amount, const uint8_t pubkey[33],
        const uint8_t ciphertext[66], const uint8_t context_hash[32]
    );

    // ---- Constants (resolved from headers at compile time) ----
    #define SECP256K1_CONTEXT_SIGN ...
    #define SECP256K1_CONTEXT_VERIFY ...
    #define SECP256K1_EC_COMPRESSED ...
    #define SECP256K1_EC_UNCOMPRESSED ...
    #define SECP256K1_COMPACT_CLAWBACK_PROOF_SIZE ...
    #define SECP256K1_COMPACT_CONVERTBACK_PROOF_SIZE ...
    #define SECP256K1_COMPACT_STANDARD_PROOF_SIZE ...
    #define kMPT_SCHNORR_PROOF_SIZE ...
    #define kMPT_SINGLE_BULLETPROOF_SIZE ...
    #define kMPT_DOUBLE_BULLETPROOF_SIZE ...
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
shared_lib_path = os.path.join(libs_dir, shared_lib_name)

# The library is only needed when we actually COMPILE the extension
# (ffibuilder.compile() during a wheel build). This module is also imported
# purely for metadata — e.g. `build --sdist`, whose isolated env has no
# compiled natives — so a missing library here must NOT abort the import.
# We warn instead; the linker enforces presence at wheel-compile time.
if not os.path.exists(shared_lib_path):
    print(
        f"WARNING: mpt-crypto shared library not found at {shared_lib_path}. "
        f"This is required only when building a wheel (ffibuilder.compile); "
        f"source-only builds (sdist) are unaffected. Run "
        f"./xrpl/ext/confidential/setup_mpt_crypto.sh download to fetch it.",
        file=sys.stderr,
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
    # MSVC links against the import library mpt-crypto.lib, resolved from
    # library_dirs (libs/win32); the matching mpt-crypto.dll is loaded at
    # runtime (see crypto_bindings._preload_shared_library).
    libraries = ["mpt-crypto"]

ffibuilder.set_source(
    "_mpt_crypto",
    """
    /* Real headers — the C compiler validates every cdef signature above
       against the actual library ABI. mpt_utility.h pulls in secp256k1_mpt.h,
       mpt_protocol.h, secp256k1.h, stdbool.h and stddef.h. */
    #include <stdint.h>
    #include <secp256k1.h>
    #include <secp256k1_mpt.h>
    #include "utility/mpt_utility.h"
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
