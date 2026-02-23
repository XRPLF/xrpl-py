#ifndef SECP256K1_MPT_H
#define SECP256K1_MPT_H

#include <secp256k1.h>
#include <stdint.h>

#ifdef __cplusplus
extern "C" {
#endif

/**
 * @brief Generates a new secp256k1 key pair.
 */
SECP256K1_API int secp256k1_elgamal_generate_keypair(
        const secp256k1_context* ctx,
        unsigned char* privkey,
        secp256k1_pubkey* pubkey
);

/**
 * @brief Encrypts a 64-bit amount using ElGamal.
 */
SECP256K1_API int secp256k1_elgamal_encrypt(
        const secp256k1_context* ctx,
        secp256k1_pubkey* c1,
        secp256k1_pubkey* c2,
        const secp256k1_pubkey* pubkey_Q,
        uint64_t amount,
        const unsigned char* blinding_factor
);

/**
 * @brief Decrypts an ElGamal ciphertext to recover the amount.
 */
SECP256K1_API int secp256k1_elgamal_decrypt(
        const secp256k1_context* ctx,
        uint64_t* amount,
        const secp256k1_pubkey* c1,
        const secp256k1_pubkey* c2,
        const unsigned char* privkey
);

/**
 * @brief Homomorphically adds two ElGamal ciphertexts.
 */
SECP256K1_API int secp256k1_elgamal_add(
        const secp256k1_context* ctx,
        secp256k1_pubkey* sum_c1,
        secp256k1_pubkey* sum_c2,
        const secp256k1_pubkey* a_c1,
        const secp256k1_pubkey* a_c2,
        const secp256k1_pubkey* b_c1,
        const secp256k1_pubkey* b_c2
);

/**
 * @brief Homomorphically subtracts two ElGamal ciphertexts.
 */
SECP256K1_API int secp256k1_elgamal_subtract(
        const secp256k1_context* ctx,
        secp256k1_pubkey* diff_c1,
        secp256k1_pubkey* diff_c2,
        const secp256k1_pubkey* a_c1,
        const secp256k1_pubkey* a_c2,
        const secp256k1_pubkey* b_c1,
        const secp256k1_pubkey* b_c2
);


/**
 * @brief Generates the canonical encrypted zero for a given MPT token instance.
 *
 * This ciphertext represents a zero balance for a specific account's holding
 * of a token defined by its MPTokenIssuanceID.
 *
 * @param[in]   ctx             A pointer to a valid secp256k1 context.
 * @param[out]  enc_zero_c1     The C1 component of the canonical ciphertext.
 * @param[out]  enc_zero_c2     The C2 component of the canonical ciphertext.
 * @param[in]   pubkey          The ElGamal public key of the account holder.
 * @param[in]   account_id      A pointer to the 20-byte AccountID.
 * @param[in]   mpt_issuance_id A pointer to the 24-byte MPTokenIssuanceID.
 *
 * @return 1 on success, 0 on failure.
 */
SECP256K1_API int generate_canonical_encrypted_zero(
        const secp256k1_context* ctx,
        secp256k1_pubkey* enc_zero_c1,
        secp256k1_pubkey* enc_zero_c2,
        const secp256k1_pubkey* pubkey,
        const unsigned char* account_id,     // 20 bytes
        const unsigned char* mpt_issuance_id // 24 bytes
);


// ... (includes and previous ElGamal declarations) ...

/*
================================================================================
|                                                                              |
|           PROOF OF KNOWLEDGE OF PLAINTEXT AND RANDOMNESS                     |
|                (Chaum-Pedersen Equality Proof)                               |
================================================================================
*/

/**
 * @brief Generates a proof that an ElGamal ciphertext correctly encrypts a
 * known plaintext `m` and that the prover knows the randomness `r`.
 *
 * @param[in]   ctx             A pointer to a valid secp256k1 context object,
 * initialized for signing.
 * @param[out]  proof           A pointer to a 98-byte buffer to store the proof
 * (T1 [33 bytes] || T2 [33 bytes] || s [32 bytes]).
 * @param[in]   c1              The C1 component of the ciphertext (r*G).
 * @param[in]   c2              The C2 component of the ciphertext (m*G + r*Pk).
 * @param[in]   pk_recipient    The public key used for encryption.
 * @param[in]   amount          The known plaintext value `m`.
 * @param[in]   randomness_r    The 32-byte secret random scalar `r` used in encryption.
 * @param[in]   tx_context_id   A 32-byte unique identifier for the transaction context.
 *
 * @return 1 on success, 0 on failure.
 */
SECP256K1_API int secp256k1_equality_plaintext_prove(
        const secp256k1_context* ctx,
        unsigned char* proof,              // Output: 98 bytes
        const secp256k1_pubkey* c1,
        const secp256k1_pubkey* c2,
        const secp256k1_pubkey* pk_recipient,
        uint64_t amount,
        const unsigned char* randomness_r, // Secret input
        const unsigned char* tx_context_id // 32 bytes
);

/**
 * @brief Verifies a proof of knowledge of plaintext and randomness.
 *
 * Checks if the proof correctly demonstrates that (C1, C2) encrypts `m`
 * under `pk_recipient`.
 *
 * @param[in]   ctx             A pointer to a valid secp256k1 context object,
 * initialized for verification.
 * @param[in]   proof           A pointer to the 98-byte proof to verify.
 * @param[in]   c1              The C1 component of the ciphertext.
 * @param[in]   c2              The C2 component of the ciphertext.
 * @param[in]   pk_recipient    The public key used for encryption.
 * @param[in]   amount          The known plaintext value `m`.
 * @param[in]   tx_context_id   A 32-byte unique identifier for the transaction context.
 *
 * @return 1 if the proof is valid, 0 otherwise.
 */
SECP256K1_API int secp256k1_equality_plaintext_verify(
        const secp256k1_context* ctx,
        const unsigned char* proof,        // Input: 98 bytes
        const secp256k1_pubkey* c1,
        const secp256k1_pubkey* c2,
        const secp256k1_pubkey* pk_recipient,
        uint64_t amount,
        const unsigned char* tx_context_id // 32 bytes
);

// ... (rest of header, #endif etc.)


/*
================================================================================
|                                                                              |
|           PROOF OF EQUALITY OF SECRET PLAINTEXTS                             |
|                (Multi-Statement Chaum-Pedersen)                              |
================================================================================
*/

/**
 * @brief Generates a proof that two ciphertexts (under different keys)
 * encrypt the same secret amount 'm'.
 *
 * @param[in]   ctx             A pointer to a valid secp256k1 context.
 * @param[out]  proof_out       A pointer to a 261-byte buffer to store the proof.
 * @param[in]   R1, S1, P1      The first ciphertext (R1, S1) and its public key (P1).
 * @param[in]   R2, S2, P2      The second ciphertext (R2, S2) and its public key (P2).
 * @param[in]   amount_m        The secret common uint64_t plaintext value 'm'.
 * @param[in]   randomness_r1   The 32-byte secret random scalar 'r1' for C1.
 * @param[in]   randomness_r2   The 32-byte secret random scalar 'r2' for C2.
 * @param[in]   tx_context_id   A 32-byte unique identifier for the transaction.
 *
 * @return 1 on success, 0 on failure.
 */
SECP256K1_API int secp256k1_mpt_prove_same_plaintext(
        const secp256k1_context* ctx,
        unsigned char* proof_out,          // Output: 261 bytes
        const secp256k1_pubkey* R1, const secp256k1_pubkey* S1, const secp256k1_pubkey* P1,
        const secp256k1_pubkey* R2, const secp256k1_pubkey* S2, const secp256k1_pubkey* P2,
        uint64_t amount_m,
        const unsigned char* randomness_r1,
        const unsigned char* randomness_r2,
        const unsigned char* tx_context_id
);

/**
 * @brief Verifies a proof that two ciphertexts encrypt the same secret amount.
 *
 * @param[in]   ctx             A pointer to a valid secp256k1 context.
 * @param[in]   proof           A pointer to the 261-byte proof to verify.
 * @param[in]   R1, S1, P1      The first ciphertext (R1, S1) and its public key (P1).
 * @param[in]   R2, S2, P2      The second ciphertext (R2, S2) and its public key (P2).
 * @param[in]   tx_context_id   A 32-byte unique identifier for the transaction.
 *
 * @return 1 if the proof is valid, 0 otherwise.
 */
SECP256K1_API int secp256k1_mpt_verify_same_plaintext(
        const secp256k1_context* ctx,
        const unsigned char* proof,        // Input: 261 bytes
        const secp256k1_pubkey* R1, const secp256k1_pubkey* S1, const secp256k1_pubkey* P1,
        const secp256k1_pubkey* R2, const secp256k1_pubkey* S2, const secp256k1_pubkey* P2,
        const unsigned char* tx_context_id
);



/**
 * @brief Calculates the expected proof size for a given number of ciphertexts.
 */
SECP256K1_API size_t secp256k1_mpt_prove_same_plaintext_multi_size(size_t n_ciphertexts);

/**
 * @brief Generates a proof that N ciphertexts encrypt the same secret amount 'm'.
 *
 * @param[in]   ctx             A pointer to a valid secp256k1 context.
 * @param[out]  proof_out       A pointer to a buffer to store the proof.
 * @param[in,out] proof_len     Input: buffer size. Output: actual proof size.
 * @param[in]   amount_m        The secret common uint64_t plaintext value 'm'.
 * @param[in]   n_ciphertexts   The number (N) of ciphertexts.
 * @param[in]   R_array         Array of N 'R' points (C1 components).
 * @param[in]   S_array         Array of N 'S' points (C2 components).
 * @param[in]   Pk_array        Array of N recipient public keys.
 * @param[in]   r_array         Array of N 32-byte secret scalars (randomness).
 * @param[in]   tx_context_id   32-byte unique transaction identifier.
 *
 * @return 1 on success, 0 on failure.
 */
SECP256K1_API int secp256k1_mpt_prove_same_plaintext_multi(
        const secp256k1_context* ctx,
        unsigned char* proof_out,
        size_t* proof_len,
        uint64_t amount_m,
        size_t n_ciphertexts,
        const secp256k1_pubkey* R_array,
        const secp256k1_pubkey* S_array,
        const secp256k1_pubkey* Pk_array,
        const unsigned char* r_array, // Flat array: r1 || r2 || ... (N * 32 bytes)
        const unsigned char* tx_context_id
);

/**
 * @brief Verifies a proof that N ciphertexts encrypt the same secret amount.
 */
SECP256K1_API int secp256k1_mpt_verify_same_plaintext_multi(
        const secp256k1_context* ctx,
        const unsigned char* proof,
        size_t proof_len,
        size_t n_ciphertexts,
        const secp256k1_pubkey* R_array,
        const secp256k1_pubkey* S_array,
        const secp256k1_pubkey* Pk_array,
        const unsigned char* tx_context_id
);


/**
 * @brief Computes a Pedersen Commitment: C = value*G + blinding_factor*Pk_base.
 *
 * This function creates the commitment point (C) that the Bulletproof proves
 * the range of. Pk_base is the dynamic secondary generator (H).
 *
 * @param[in]   ctx             A pointer to the context.
 * @param[out]  commitment_C    The resulting commitment point C.
 * @param[in]   value           The secret amount v (uint64_t).
 * @param[in]   blinding_factor The secret randomness r (32 bytes).
 * @param[in]   pk_base         The recipient's public key (used as the H generator).
 *
 * @return 1 on success, 0 on failure.
 */
SECP256K1_API int secp256k1_bulletproof_create_commitment(
        const secp256k1_context* ctx,
        secp256k1_pubkey* commitment_C,
        uint64_t value,
        const unsigned char* blinding_factor,
        const secp256k1_pubkey* pk_base
);


int secp256k1_bulletproof_prove(
        const secp256k1_context* ctx,
        unsigned char* proof_out,
        size_t* proof_len,
        uint64_t value,
        const unsigned char* blinding_factor,
        const secp256k1_pubkey* pk_base,
        const unsigned char* context_id,    /* <--- AND HERE */
        unsigned int proof_type
);


int secp256k1_bulletproof_verify(
        const secp256k1_context* ctx,
        const secp256k1_pubkey* G_vec,
        const secp256k1_pubkey* H_vec,
        const unsigned char* proof,
        size_t proof_len,
        const secp256k1_pubkey* commitment_C,
        const secp256k1_pubkey* pk_base, /* This is generator H */
        const unsigned char* context_id
);
/**
 * @brief Proves the link between an ElGamal ciphertext and a Pedersen commitment.
 * * Formal Statement: Knowledge of (m, r, rho) such that:
 * C1 = r*G, C2 = m*G + r*Pk, and PCm = m*G + rho*H.
 * * @param ctx         Pointer to a secp256k1 context object.
 * @param proof       [OUT] Pointer to 195-byte buffer for the proof output.
 * @param c1          Pointer to the ElGamal C1 point (r*G).
 * @param c2          Pointer to the ElGamal C2 point (m*G + r*Pk).
 * @param pk          Pointer to the recipient's public key.
 * @param pcm         Pointer to the Pedersen Commitment (m*G + rho*H).
 * @param amount      The plaintext amount (m).
 * @param r           The 32-byte secret ElGamal blinding factor.
 * @param rho         The 32-byte secret Pedersen blinding factor.
 * @param context_id  32-byte unique transaction context identifier.
 * @return 1 on success, 0 on failure.
 */
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
        const unsigned char* context_id);

/**
 * @brief Verifies the link proof between ElGamal and Pedersen commitments.
 * * @return 1 if the proof is valid, 0 otherwise.
 */
int secp256k1_elgamal_pedersen_link_verify(
        const secp256k1_context* ctx,
        const unsigned char* proof,
        const secp256k1_pubkey* c1,
        const secp256k1_pubkey* c2,
        const secp256k1_pubkey* pk,
        const secp256k1_pubkey* pcm,
        const unsigned char* context_id);

/**
 * Verifies that (c1, c2) is a valid ElGamal encryption of 'amount'
 * for 'pubkey_Q' using the revealed 'blinding_factor'.
 */
int secp256k1_elgamal_verify_encryption(
        const secp256k1_context* ctx,
        const secp256k1_pubkey* c1,
        const secp256k1_pubkey* c2,
        const secp256k1_pubkey* pubkey_Q,
        uint64_t amount,
        const unsigned char* blinding_factor
);

/** Proof of Knowledge of Secret Key for Registration */
int secp256k1_mpt_pok_sk_prove(
        const secp256k1_context* ctx,
        unsigned char* proof,           /* Expected size: 65 bytes */
        const secp256k1_pubkey* pk,
        const unsigned char* sk,
        const unsigned char* context_id
);

int secp256k1_mpt_pok_sk_verify(
        const secp256k1_context* ctx,
        const unsigned char* proof,     /* Expected size: 65 bytes */
        const secp256k1_pubkey* pk,
        const unsigned char* context_id
);

/**
 * Compute a Pedersen Commitment: PC = m*G + rho*H
 * Returns 1 on success, 0 on failure.
 */
int secp256k1_mpt_pedersen_commit(
        const secp256k1_context* ctx,
        secp256k1_pubkey* commitment,
        uint64_t amount,
        const unsigned char* blinding_factor_rho  /* 32 bytes */
);

/** Get the standardized H generator for Pedersen Commitments */
int secp256k1_mpt_get_h_generator(const secp256k1_context* ctx, secp256k1_pubkey* h);

/**
 * @brief Generates a vector of N independent NUMS generators.
 */
int secp256k1_mpt_get_generator_vector(
        const secp256k1_context* ctx,
        secp256k1_pubkey* vec,
        size_t n,
        const unsigned char* label,
        size_t label_len
);

void secp256k1_mpt_scalar_add(unsigned char *res, const unsigned char *a, const unsigned char *b);
void secp256k1_mpt_scalar_mul(unsigned char *res, const unsigned char *a, const unsigned char *b);
void secp256k1_mpt_scalar_inverse(unsigned char *res, const unsigned char *in);
void secp256k1_mpt_scalar_negate(unsigned char *res, const unsigned char *in);
void secp256k1_mpt_scalar_reduce32(unsigned char out32[32], const unsigned char in32[32]);


/**
 * Returns the size of the serialized proof for N recipients.
 * Size: (1 + N) * 33 bytes for points + 2 * 32 bytes for scalars.
 */
size_t secp256k1_mpt_proof_equality_shared_r_size(size_t n);

/**
 * Generates a proof that multiple ciphertexts encrypt the same amount m
 * using the SAME shared randomness r.
 */
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

/**
 * Verifies the proof of equality with shared randomness.
 */
int secp256k1_mpt_verify_equality_shared_r(
        const secp256k1_context* ctx,
        const unsigned char* proof,
        size_t n,
        const secp256k1_pubkey* C1,
        const secp256k1_pubkey* C2_vec,
        const secp256k1_pubkey* Pk_vec,
        const unsigned char* context_id
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
        const secp256k1_pubkey* G_vec,              /* length n = 64*m */
        const secp256k1_pubkey* H_vec,              /* length n = 64*m */
        const unsigned char* proof,
        size_t proof_len,
        const secp256k1_pubkey* commitment_C_vec,   /* length m */
        size_t m,
        const secp256k1_pubkey* pk_base,
        const unsigned char* context_id
);





#ifdef __cplusplus
}
#endif

#endif // SECP256K1_MPT_H
