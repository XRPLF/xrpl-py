#ifndef MPT_PROTOCOL_H
#define MPT_PROTOCOL_H

#include <stdint.h>

#ifdef __cplusplus
extern "C" {
#endif

// XRPL Transaction Types, the number MUST match rippled's definitions
#define kCONFIDENTIAL_MPT_CONVERT 85
#define kCONFIDENTIAL_MPT_MERGE_INBOX 86
#define kCONFIDENTIAL_MPT_CONVERT_BACK 87
#define kCONFIDENTIAL_MPT_SEND 88
#define kCONFIDENTIAL_MPT_CLAWBACK 89

// General crypto primitive sizes in bytes
#define kMPT_HALF_SHA_SIZE 32
#define kMPT_PUBKEY_SIZE 33
#define kMPT_PRIVKEY_SIZE 32
#define kMPT_BLINDING_FACTOR_SIZE 32
// secp256k1 scalar (challenge / response / nonce) size in bytes.
// Numerically equal to kMPT_HALF_SHA_SIZE; use this name when the value is a
// scalar in Z_q rather than a hash output.
#define kMPT_SCALAR_SIZE 32

// ElGamal & Pedersen primitive sizes in bytes
#define kMPT_ELGAMAL_CIPHER_SIZE 33
#define kMPT_ELGAMAL_TOTAL_SIZE 66
#define kMPT_PEDERSEN_COMMIT_SIZE 33

// Proof sizes in bytes
#define kMPT_SCHNORR_PROOF_SIZE 64
#define kMPT_SINGLE_BULLETPROOF_SIZE 688
#define kMPT_DOUBLE_BULLETPROOF_SIZE 754

// Context hash size
#define kMPT_ZKP_CONTEXT_HASH_SIZE 74

// Account ID size in bytes
#define kMPT_ACCOUNT_ID_SIZE 20

// MPTokenIssuance ID size in bytes
#define kMPT_ISSUANCE_ID_SIZE 24

#ifdef __cplusplus
}
#endif

#endif  // MPT_PROTOCOL_H
