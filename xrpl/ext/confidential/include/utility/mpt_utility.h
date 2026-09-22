#ifndef MPT_UTILITY_H
#define MPT_UTILITY_H

#include <mpt_protocol.h>
#include <secp256k1.h>
#include <secp256k1_mpt.h>
#include <stdbool.h>
#include <stddef.h>

#ifdef __cplusplus
extern "C" {
#endif

/**
 * @brief Represents a unique 24-byte MPT issuance ID.
 */
typedef struct
{
    uint8_t bytes[kMPT_ISSUANCE_ID_SIZE];
} mpt_issuance_id;

/**
 * @brief Represents a 20-byte account ID.
 *
 * - bytes: Raw 20-byte array containing the AccountID.
 */
typedef struct account_id
{
    uint8_t bytes[kMPT_ACCOUNT_ID_SIZE];
} account_id;

/**
 * @brief Represents a participant in a Confidential Send transaction.
 *
 * - pubkey: The 33-byte compressed secp256k1 public key.
 * - ciphertext: The 66-byte ElGamal encrypted amount.
 */
typedef struct mpt_confidential_participant
{
    uint8_t pubkey[kMPT_PUBKEY_SIZE];
    uint8_t ciphertext[kMPT_ELGAMAL_TOTAL_SIZE];
} mpt_confidential_participant;

/**
 * @brief Parameters required to generate a Pedersen Linkage Proof.
 *
 * - pedersen_commitment: The 64-byte Pedersen commitment.
 * - amount: The actual numeric value being committed.
 * - ciphertext: The 66-byte buffer containing the encrypted amount.
 * - blinding_factor: The 32-byte secret value used to blind the commitment.
 */
typedef struct mpt_pedersen_proof_params
{
    uint8_t pedersen_commitment[kMPT_PEDERSEN_COMMIT_SIZE];
    uint64_t amount;
    uint8_t ciphertext[kMPT_ELGAMAL_TOTAL_SIZE];
    uint8_t blinding_factor[kMPT_BLINDING_FACTOR_SIZE];
} mpt_pedersen_proof_params;

/**
 * @brief Returns a globally shared secp256k1 context.
 */
secp256k1_context*
mpt_secp256k1_context();

/**
 * @brief Context Hash for ConfidentialMPTConvert.
 */
int
mpt_get_convert_context_hash(
    account_id account,
    mpt_issuance_id iss,
    uint32_t sequence,
    uint8_t out_hash[kMPT_HALF_SHA_SIZE]);

/**
 * @brief Context Hash for ConfidentialMPTConvertBack.
 */
int
mpt_get_convert_back_context_hash(
    account_id acc,
    mpt_issuance_id iss,
    uint32_t seq,
    uint32_t ver,
    uint8_t out_hash[kMPT_HALF_SHA_SIZE]);

/**
 * @brief Context Hash for ConfidentialMPTSend.
 */
int
mpt_get_send_context_hash(
    account_id acc,
    mpt_issuance_id iss,
    uint32_t seq,
    account_id dest,
    uint32_t ver,
    uint8_t out_hash[kMPT_HALF_SHA_SIZE]);

/**
 * @brief Context Hash for ConfidentialMPTClawback.
 */
int
mpt_get_clawback_context_hash(
    account_id acc,
    mpt_issuance_id iss,
    uint32_t seq,
    account_id holder,
    uint8_t out_hash[kMPT_HALF_SHA_SIZE]);

/* ============================================================================
 * Key & Ciphertext Utilities
 * ============================================================================ */

/**
 * @brief Parses a 66-byte buffer into two internal secp256k1 public keys.
 * @param buffer [in] 66-byte buffer containing two points.
 * @param out1   [out] First internal public key (C1).
 * @param out2   [out] Second internal public key (C2).
 * @return true on success, false if parsing fails.
 */
bool
mpt_make_ec_pair(
    uint8_t const buffer[kMPT_ELGAMAL_TOTAL_SIZE],
    secp256k1_pubkey* out1,
    secp256k1_pubkey* out2);

/**
 * @brief Serializes two internal secp256k1 public keys into a 66-byte buffer.
 * @param in1   [in] Internal format of the first point (C1).
 * @param in2   [in] Internal format of the second point (C2).
 * @param out   [out] 66-byte buffer to write the serialized points.
 * @return true if both points were valid and successfully serialized, false otherwise.
 */
bool
mpt_serialize_ec_pair(
    secp256k1_pubkey const* in1,
    secp256k1_pubkey const* in2,
    uint8_t out[kMPT_ELGAMAL_TOTAL_SIZE]);

/**
 * @brief Generates a new Secp256k1 ElGamal keypair.
 * @param out_privkey [out] A 32-byte buffer for private key.
 * @param out_pubkey  [out] A 33-byte buffer for public key.
 * @return 0 on success, -1 on failure.
 */
int
mpt_generate_keypair(uint8_t* out_privkey, uint8_t* out_pubkey);

/**
 * @brief Generates a 32-byte blinding factor.
 * @param out_factor [out] A 32-byte buffer to store the blinding factor.
 * @return 0 on success, -1 on failure.
 */
int
mpt_generate_blinding_factor(uint8_t out_factor[kMPT_BLINDING_FACTOR_SIZE]);

/**
 * @brief Encrypts an uint64 amount using an ElGamal public key.
 * @param amount           [in]  The integer value to encrypt.
 * @param pubkey           [in]  The 33-byte public key.
 * @param blinding_factor  [in]  The 32-byte random blinding factor (scalar r).
 * @param out_ciphertext   [out] A 66-byte buffer to store the resulting ciphertext (C1, C2).
 * @return 0 on success, -1 on failure.
 */
int
mpt_encrypt_amount(
    uint64_t amount,
    uint8_t const pubkey[kMPT_PUBKEY_SIZE],
    uint8_t const blinding_factor[kMPT_BLINDING_FACTOR_SIZE],
    uint8_t out_ciphertext[kMPT_ELGAMAL_TOTAL_SIZE]);

/**
 * @brief Decrypts an MPT amount from a ciphertext pair.
 * @param ciphertext [in]  A 66-byte buffer containing the two points (C1, C2).
 * @param privkey    [in]  The 32-byte private key.
 * @param out_amount [out] Pointer to store the decrypted uint64_t amount.
 * @param range_low  [in]  Lower bound of the search range (inclusive).
 * @param range_high [in]  Upper bound of the search range (inclusive).
 *                         Must satisfy range_low <= range_high and
 *                         range_high != UINT64_MAX.
 * @return 0 on success, -1 on failure, -2 if range_low > range_high or
 *         range_high == UINT64_MAX.
 * @note Performance scales linearly with (range_high - range_low). A range of [0, 1,000,000] takes
 * approximately 3 seconds on Apple Silicon. Do not pass arbitrarily large ranges.
 */
int
mpt_decrypt_amount(
    uint8_t const ciphertext[kMPT_ELGAMAL_TOTAL_SIZE],
    uint8_t const privkey[kMPT_PRIVKEY_SIZE],
    uint64_t* out_amount,
    uint64_t range_low,
    uint64_t range_high);

/* ============================================================================
 * ZKProof Generation
 * ============================================================================ */

/**
 * @brief Generates a Schnorr Proof of Knowledge for a Confidential MPT conversion.
 *
 * This proof is used in 'ConfidentialMPTConvert' transactions to prove the
 * sender possesses the private key associated with the account, binding it
 * to the specific transaction via the ctx_hash.
 *
 * @param pubkey    [in]  33-byte public key of the account.
 * @param privkey   [in]  32-byte private key of the account.
 * @param ctx_hash  [in]  32-byte hash of the transaction (challenge).
 * @param out_proof [out] 64-byte buffer to store the compact Schnorr proof.
 * @return 0 on success, -1 on failure.
 */
int
mpt_get_convert_proof(
    uint8_t const pubkey[kMPT_PUBKEY_SIZE],
    uint8_t const privkey[kMPT_PRIVKEY_SIZE],
    uint8_t const ctx_hash[kMPT_HALF_SHA_SIZE],
    uint8_t out_proof[kMPT_SCHNORR_PROOF_SIZE]);

/**
 * @brief Computes a Pedersen Commitment point for Confidential MPT.
 * @param amount           [in]  The 64-bit unsigned integer value to commit.
 * @param blinding_factor  [in]  A 32-byte secret scalar (rho) used to hide the amount.
 * @param out_commitment   [out] A 33-byte buffer to store the commitment
 */
int
mpt_get_pedersen_commitment(
    uint64_t amount,
    uint8_t const blinding_factor[kMPT_BLINDING_FACTOR_SIZE],
    uint8_t out_commitment[kMPT_PEDERSEN_COMMIT_SIZE]);

/**
 * @brief Generates proof for ConfidentialMPTSend.
 *
 * Produces a compact AND-composed sigma proof (192 bytes) that simultaneously
 * proves ciphertext equality, Pedersen commitment linkage, and balance ownership
 * under a single Fiat-Shamir challenge, followed by an aggregated Bulletproof
 * range proof (754 bytes). Total proof size is fixed at 946 bytes.
 *
 * pc_m must be computed as m*G + r*H using tx_blinding_factor as the blinding
 * factor (not an independent scalar), since the compact sigma proof binds pc_m
 * to the ciphertext randomness r.
 *
 * @param priv               [in] The sender's 32-byte private key.
 * @param pub                [in] The sender's 33-byte public key.
 * @param amount             [in] The amount being sent.
 * @param participants         [in] List of participants, including Sender, Dest, Issuer,
 * Auditor(optional).
 * @param n_participants       [in] Number of participants (3 or 4).
 * @param tx_blinding_factor [in] The ElGamal randomness r (also blinding factor for pc_m).
 * @param context_hash       [in] The 32-byte context hash.
 * @param amount_commitment  [in] Pedersen commitment pc_m = m*G + r*H.
 * @param balance_params     [in] Includes pedersen_commitment (pc_b), amount (balance),
 *                                blinding_factor (rho), and ciphertext (b1||b2).
 * @param out_proof          [out] Buffer to receive the proof blob.
 * @param out_len            [in/out] In: capacity (must be >= 946). Out: bytes written.
 * @return 0 on success, -1 on failure.
 */
int
mpt_get_confidential_send_proof(
    uint8_t const priv[kMPT_PRIVKEY_SIZE],
    uint8_t const pub[kMPT_PUBKEY_SIZE],
    uint64_t amount,
    mpt_confidential_participant const* participants,
    size_t n_participants,
    uint8_t const tx_blinding_factor[kMPT_BLINDING_FACTOR_SIZE],
    uint8_t const context_hash[kMPT_HALF_SHA_SIZE],
    uint8_t const amount_commitment[kMPT_PEDERSEN_COMMIT_SIZE],
    mpt_pedersen_proof_params const* balance_params,
    uint8_t* out_proof,
    size_t* out_len);

/**
 * @brief Generates proof for ConfidentialMPTConvertBack.
 *
 * Produces a compact AND-composed sigma proof (128 bytes) over the balance
 * witness (b, rho, priv), followed by a single Bulletproof range proof (688
 * bytes) over the remainder commitment pc_rem = pc_b - m*G.
 * Total proof size: 816 bytes (SECP256K1_COMPACT_CONVERTBACK_PROOF_SIZE +
 * kMPT_SINGLE_BULLETPROOF_SIZE).
 *
 * @param priv         [in] The holder's 32-byte private key.
 * @param pub          [in] The holder's 33-byte public key.
 * @param context_hash [in] The 32-byte context hash binding the proof to the transaction.
 * @param amount       [in] The publicly revealed conversion amount m.
 * @param params       [in] Includes pedersen_commitment (pc_b), blinding_factor (rho),
 *                          amount (balance b), and ciphertext (b1||b2).
 * @param out_proof    [out] 816-byte buffer for the compact sigma proof and range proof.
 * @return 0 on success, -1 on failure.
 */
int
mpt_get_convert_back_proof(
    uint8_t const priv[kMPT_PRIVKEY_SIZE],
    uint8_t const pub[kMPT_PUBKEY_SIZE],
    uint8_t const context_hash[kMPT_HALF_SHA_SIZE],
    uint64_t const amount,
    mpt_pedersen_proof_params const* params,
    uint8_t out_proof[SECP256K1_COMPACT_CONVERTBACK_PROOF_SIZE + kMPT_SINGLE_BULLETPROOF_SIZE]);

/**
 * @brief Generates proof for ConfidentialMPTClawback.
 * @param priv         [in] The issuer's 32-byte private key.
 * @param pub          [in] The issuer's 33-byte compressed public key.
 * @param context_hash [in] The 32-byte context hash binding the proof to the transaction.
 * @param amount       [in] The publicly known amount to be clawed back.
 * @param ciphertext   [in] The 66-byte sfIssuerEncryptedBalance blob from the ledger.
 * @param out_proof    [out] 64-byte buffer for the compact sigma proof.
 * @return 0 on success, -1 on failure.
 */
int
mpt_get_clawback_proof(
    uint8_t const priv[kMPT_PRIVKEY_SIZE],
    uint8_t const pub[kMPT_PUBKEY_SIZE],
    uint8_t const context_hash[kMPT_HALF_SHA_SIZE],
    uint64_t const amount,
    uint8_t const ciphertext[kMPT_ELGAMAL_TOTAL_SIZE],
    uint8_t out_proof[SECP256K1_COMPACT_CLAWBACK_PROOF_SIZE]);

/* ============================================================================
 * Non-ZKP Validation
 * ============================================================================ */

/**
 * @brief Verifies that the ElGamal ciphertexts held by all participants encrypt
 * the same revealed plaintext amount under the given blinding factor.
 *
 * @param amount          [in] Actual numeric amount to verify against.
 * @param blinding_factor [in] The ElGamal randomness r used to produce all ciphertexts.
 * @param holder          [in] Holder's public key and ciphertext.
 * @param issuer          [in] Issuer's public key and ciphertext.
 * @param auditor         [in] Auditor's public key and ciphertext, optional.
 * @return 0 on success, -1 on failure.
 */
int
mpt_verify_revealed_amount(
    uint64_t const amount,
    uint8_t const blinding_factor[kMPT_BLINDING_FACTOR_SIZE],
    mpt_confidential_participant const* holder,
    mpt_confidential_participant const* issuer,
    mpt_confidential_participant const* auditor);

/* ============================================================================
 * ZKProof Verifications for Each Transaction
 * ============================================================================ */

/**
 * @brief Verify proof for ConfidentialMPTConvert.
 *
 * Proves that the sender possesses the private key for the provided public key.
 *
 * @param proof        [in] The 64-byte compact Schnorr proof.
 * @param pubkey       [in] The 33-byte compressed ElGamal public key.
 * @param context_hash [in] The 32-byte transaction context hash.
 * @return 0 on success, -1 on failure.
 */
int
mpt_verify_convert_proof(
    uint8_t const proof[kMPT_SCHNORR_PROOF_SIZE],
    uint8_t const pubkey[kMPT_PUBKEY_SIZE],
    uint8_t const context_hash[kMPT_HALF_SHA_SIZE]);

/**
 * @brief Verify proof for ConfidentialMPTConvertBack
 *
 * Proves that the hidden balance matches the commitment and that
 * subtracting the transparent amount results in a non-negative balance.
 *
 * @param proof              [in] 816-byte proof blob (compact sigma || Bulletproof).
 * @param pubkey             [in] The holder's 33-byte ElGamal public key.
 * @param ciphertext         [in] The holder's 66-byte balance ciphertext.
 * @param balance_commitment [in] The 33-byte Pedersen commitment to the balance.
 * @param amount             [in] The publicly revealed conversion amount m.
 * @param context_hash       [in] The 32-byte transaction context hash.
 * @return 0 on success, -1 on failure.
 */
int
mpt_verify_convert_back_proof(
    uint8_t const proof[SECP256K1_COMPACT_CONVERTBACK_PROOF_SIZE + kMPT_SINGLE_BULLETPROOF_SIZE],
    uint8_t const pubkey[kMPT_PUBKEY_SIZE],
    uint8_t const ciphertext[kMPT_ELGAMAL_TOTAL_SIZE],
    uint8_t const balance_commitment[kMPT_PEDERSEN_COMMIT_SIZE],
    uint64_t const amount,
    uint8_t const context_hash[kMPT_HALF_SHA_SIZE]);

/**
 * @brief Verify proof for ConfidentialMPTSend.
 *
 * Verifies the compact AND-composed sigma proof (first 192 bytes) that proves
 * ciphertext correctness, Pedersen commitment linkage, and balance ownership,
 * followed by an aggregated Bulletproof range proof (next 754 bytes).
 * Proof size is fixed at 946 bytes.
 *
 * @param proof                      [in] 946-byte proof blob (compact sigma || Bulletproof).
 * @param participants               [in] List of participants' public keys and ciphertexts.
 *                                        participants[0] is the sender.
 * @param n_participants             [in] Number of participants (3 or 4).
 * @param sender_spending_ciphertext [in] The sender's on-ledger balance ciphertext (b1||b2).
 * @param amount_commitment          [in] Pedersen commitment pc_m to the transfer amount.
 * @param balance_commitment         [in] Pedersen commitment pc_b to the sender's balance.
 * @param context_hash               [in] The 32-byte transaction context hash.
 * @return 0 on success, -1 on failure.
 */
int
mpt_verify_send_proof(
    uint8_t const* proof,
    mpt_confidential_participant const* participants,
    uint8_t const n_participants,
    uint8_t const sender_spending_ciphertext[kMPT_ELGAMAL_TOTAL_SIZE],
    uint8_t const amount_commitment[kMPT_PEDERSEN_COMMIT_SIZE],
    uint8_t const balance_commitment[kMPT_PEDERSEN_COMMIT_SIZE],
    uint8_t const context_hash[kMPT_HALF_SHA_SIZE]);

/**
 * @brief Verify proof for ConfidentialMPTClawback.
 *
 * Proves that a ciphertext, when decrypted by the issuer, results in exactly the plaintext amount
 * specified in the transaction.
 *
 * @param proof        [in] The 64-byte compact sigma proof.
 * @param amount       [in] The publicly known amount to be clawed back.
 * @param pubkey       [in] The issuer's 33-byte compressed public key.
 * @param ciphertext   [in] The 66-byte sfIssuerEncryptedBalance blob associated with the holder's
 *                         account on the ledger.
 * @param context_hash [in] The 32-byte transaction context hash.
 * @return 0 on success, -1 on failure.
 */
int
mpt_verify_clawback_proof(
    uint8_t const proof[SECP256K1_COMPACT_CLAWBACK_PROOF_SIZE],
    uint64_t const amount,
    uint8_t const pubkey[kMPT_PUBKEY_SIZE],
    uint8_t const ciphertext[kMPT_ELGAMAL_TOTAL_SIZE],
    uint8_t const context_hash[kMPT_HALF_SHA_SIZE]);

/**
 * @brief Helper function to substract a transparent amount from a hidden commitment.
 *
 * @param commitment_in  [in] The 33-byte starting Pedersen commitment.
 * @param amount         [in] The integer amount to subtract.
 * @param commitment_out [out] The resulting 33-byte remainder commitment.
 * @return 0 on success, -1 on failure.
 */
int
mpt_compute_convert_back_remainder(
    uint8_t const commitment_in[kMPT_PEDERSEN_COMMIT_SIZE],
    uint64_t amount,
    uint8_t commitment_out[kMPT_PEDERSEN_COMMIT_SIZE]);

/**
 * @brief Generic verifier for aggregated Bulletproofs (Range Proofs).
 *
 * @param proof                  [in] The serialized Bulletproof buffer.
 * @param proof_len              [in] The length of the proof buffer in bytes.
 * @param compressed_commitments [in] An array of pointers to the 33-byte Pedersen commitments.
 * @param m                      [in] The number of commitments to verify.
 * @param context_hash           [in] The 32-byte context hash binding the proof to the transaction.
 * @return 0 on success, -1 on failure.
 */
int
mpt_verify_aggregated_bulletproof(
    uint8_t const* proof,
    size_t proof_len,
    uint8_t const** compressed_commitments,
    size_t m,
    uint8_t const context_hash[kMPT_HALF_SHA_SIZE]);

/**
 * @brief Verifies that the sending amount and remaining balance reside within the valid range from
 * 0 to 2^64-1.
 *
 * @param ctx                [in] secp256k1-zkp context.
 * @param proof              [in] 754-byte Double Bulletproof.
 * @param amount_commitment  [in] Pedersen commitment to the transfer amount.
 * @param balance_commitment [in] Pedersen commitment to the sender's total balance.
 * @param context_hash       [in] 32-byte transaction context hash.
 * @return 0 on success, -1 on failure.
 */
int
mpt_verify_send_range_proof(
    uint8_t const proof[kMPT_DOUBLE_BULLETPROOF_SIZE],
    uint8_t const amount_commitment[kMPT_PEDERSEN_COMMIT_SIZE],
    uint8_t const balance_commitment[kMPT_PEDERSEN_COMMIT_SIZE],
    uint8_t const context_hash[kMPT_HALF_SHA_SIZE]);

#ifdef __cplusplus
}
#endif
#endif
