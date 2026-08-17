"""
Build script for mpt-crypto C library Python bindings using cffi.
"""

import os
import platform
import sys

from cffi import FFI

ffibuilder = FFI()

# Define the C API that we want to expose to Python
ffibuilder.cdef("""
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

    // NOTE on vanilla upstream secp256k1 symbols. secp256k1 is statically linked
    // INTO the extension (via the self-contained mpt-crypto archive), so its
    // public API is bound directly on every platform — including Windows, where a
    // DLL would not have re-exported these symbols. secp256k1_ec_pubkey_parse is
    // therefore declared unconditionally (further down), so
    // create_bulletproof/verify_bulletproof work everywhere. We still use the
    // exported mpt_secp256k1_context() for the shared context rather than
    // secp256k1_context_create/_destroy. Keep the typedefs above — the bulletproof
    // / mpt_ signatures below still use them.

    // Globally shared secp256k1 context owned by mpt-crypto (do not destroy).
    secp256k1_context* mpt_secp256k1_context(void);

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
""")

# ──────────────────────────────────────────────────────────────────────────────
# Locate the self-contained STATIC archive and link it INTO the extension.
#
# mpt-crypto ships a self-contained static archive (secp256k1 + OpenSSL merged
# in). We statically link it into the _mpt_crypto extension, so the compiled
# .so/.pyd is self-contained: no shared library to load at runtime, no rpath,
# and — on Windows — no LoadLibrary preload. secp256k1's API is linked directly,
# so secp256k1_ec_pubkey_parse is available on every platform (the old Windows
# DLL did not re-export it).
#
# Expected layout (staged by the before-all step, per platform):
#   libs/linux/libmpt-crypto.a
#   libs/darwin/libmpt-crypto.a
#   libs/win32/mpt-crypto-static.lib
#   libs/<platform>/mpt-crypto-static.link-libs.txt   (system libs to co-link)
# ──────────────────────────────────────────────────────────────────────────────
script_dir = os.path.dirname(os.path.abspath(__file__))
system = platform.system().lower()

if system == "darwin":
    lib_subdir = "darwin"
    static_lib_name = "libmpt-crypto.a"
elif system == "linux":
    lib_subdir = "linux"
    static_lib_name = "libmpt-crypto.a"
elif system == "windows" or system.startswith("win"):
    lib_subdir = "win32"
    static_lib_name = "mpt-crypto-static.lib"
else:
    raise RuntimeError(f"Unsupported platform: {system}")

# secp256k1_ec_pubkey_parse is now linked directly from the static archive on
# every platform (static linking binds symbols that a DLL would not re-export),
# so declare it unconditionally — this restores commitments.create_bulletproof /
# verify_bulletproof on Windows.
ffibuilder.cdef(
    "int secp256k1_ec_pubkey_parse("
    "const secp256k1_context* ctx, secp256k1_pubkey* pubkey, "
    "const unsigned char* input, size_t inputlen);"
)

# Point serialization + ElGamal homomorphic ops — used by homomorphic.py to
# predict a confidential balance's next state (Enc(a) +/- Enc(b) = Enc(a +/- b))
# for chaining proofs across multiple confidential transfers in one Batch.
# Like secp256k1_ec_pubkey_parse, these are linked directly from the static
# archive on every platform.
ffibuilder.cdef(
    "int secp256k1_ec_pubkey_serialize("
    "const secp256k1_context* ctx, unsigned char* output, size_t* outputlen, "
    "const secp256k1_pubkey* pubkey, unsigned int flags);"
    "int secp256k1_elgamal_add("
    "const secp256k1_context* ctx, secp256k1_pubkey* sum_c1, "
    "secp256k1_pubkey* sum_c2, const secp256k1_pubkey* a_c1, "
    "const secp256k1_pubkey* a_c2, const secp256k1_pubkey* b_c1, "
    "const secp256k1_pubkey* b_c2);"
    "int secp256k1_elgamal_subtract("
    "const secp256k1_context* ctx, secp256k1_pubkey* diff_c1, "
    "secp256k1_pubkey* diff_c2, const secp256k1_pubkey* a_c1, "
    "const secp256k1_pubkey* a_c2, const secp256k1_pubkey* b_c1, "
    "const secp256k1_pubkey* b_c2);"
)

libs_dir = os.path.join(script_dir, "libs", lib_subdir)
include_dir = os.path.join(script_dir, "include")
static_lib_path = os.path.join(libs_dir, static_lib_name)
link_libs_manifest = os.path.join(libs_dir, "mpt-crypto-static.link-libs.txt")


def _read_system_libs(manifest_path: str) -> list:
    """Read the system libraries to co-link, from the archive's manifest.

    mpt-crypto emits ``mpt-crypto-static.link-libs.txt`` next to the archive —
    one library name per line (the C++ runtime + OpenSSL's OS-level deps that
    the self-contained archive still needs). Falls back to per-platform defaults
    if the manifest is absent (e.g. an older bundle).
    """
    if os.path.exists(manifest_path):
        names = []
        with open(manifest_path) as handle:
            for line in handle:
                name = line.strip()
                if name and not name.startswith("#"):
                    names.append(name)
        if names:
            return names
    if system == "darwin":
        return ["c++"]
    if system == "linux":
        return ["stdc++", "pthread", "dl", "m"]
    return [
        "crypt32",
        "ws2_32",
        "advapi32",
        "user32",
        "gdi32",
        "bcrypt",
        "legacy_stdio_definitions",
    ]


# The archive is only needed when we actually COMPILE the extension
# (ffibuilder.compile() during a wheel build). This module is also imported
# purely for metadata — e.g. `build --sdist`, whose isolated env has no
# staged natives — so a missing archive here must NOT abort the import.
# We warn instead; the linker enforces presence at wheel-compile time.
if not os.path.exists(static_lib_path):
    print(
        f"WARNING: mpt-crypto static archive not found at {static_lib_path}. "
        f"This is required only when building a wheel (ffibuilder.compile); "
        f"source-only builds (sdist) are unaffected. Run "
        f"./xrpl/ext/confidential/setup_mpt_crypto.sh download to fetch it.",
        file=sys.stderr,
    )

include_dirs = [include_dir]
# System libs the self-contained archive still needs (C++ runtime + OpenSSL's
# OS-level deps). They are linked AFTER the archive.
libraries = _read_system_libs(link_libs_manifest)

extra_compile_args = ["-fPIC"] if system == "linux" else []
extra_link_args: list = []

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
    # Statically link the whole self-contained archive INTO the extension, so the
    # compiled _mpt_crypto is standalone (no runtime shared-library dependency).
    extra_objects=[static_lib_path],
    libraries=libraries,
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
        print(f"  Static archive: {static_lib_path}")
        print(f"  Size: {os.path.getsize(static_lib_path) / (1024*1024):.1f} MB")
    finally:
        os.chdir(original_dir)
