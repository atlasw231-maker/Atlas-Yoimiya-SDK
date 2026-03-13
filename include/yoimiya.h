/*
 * Yoimiya ZK Proving SDK — C Header
 *
 * Business Source License 1.1
 * Copyright (c) 2025 Yoimiya / Atlas
 *
 * Link against: -lyoimiya (or the static/dynamic lib produced by cargo build)
 */

#ifndef YOIMIYA_H
#define YOIMIYA_H

#include <stdint.h>

#ifdef __cplusplus
extern "C" {
#endif

/* ── Opaque handles ─────────────────────────────────────────────── */

typedef struct YoimiyaSrs       YoimiyaSrs;
typedef struct YoimiyaProof     YoimiyaProof;
typedef struct YoimiyaBatchProof YoimiyaBatchProof;

/* ── SRS ────────────────────────────────────────────────────────── */

/**
 * Generate a deterministic test SRS (NOT for production).
 * @param max_degree  Maximum polynomial degree the SRS supports.
 * @return Opaque SRS handle. Free with yoimiya_free_srs().
 */
YoimiyaSrs* yoimiya_generate_test_srs(uint32_t max_degree);

/**
 * Free an SRS handle.
 */
void yoimiya_free_srs(YoimiyaSrs* srs);

/* ── Prove ──────────────────────────────────────────────────────── */

/**
 * Prove a test circuit (for benchmarking / integration testing).
 *
 * @param num_constraints  Number of R1CS constraints.
 * @param witness_data     Array of uint64 witness values.
 * @param witness_len      Length of witness_data array.
 * @param srs              SRS handle from yoimiya_generate_test_srs().
 * @return Proof handle, or NULL on error. Free with yoimiya_free_proof().
 */
YoimiyaProof* yoimiya_prove_test(
    uint32_t num_constraints,
    const uint64_t* witness_data,
    uint32_t witness_len,
    const YoimiyaSrs* srs
);

/**
 * Prove an R1CS circuit loaded from a file.
 *
 * @param r1cs_path   Null-terminated path to the .r1cs file.
 * @param witness_data Array of uint64 witness values.
 * @param witness_len  Length of witness_data array.
 * @param srs          SRS handle.
 * @return Proof handle, or NULL on error. Free with yoimiya_free_proof().
 */
YoimiyaProof* yoimiya_prove_r1cs(
    const char* r1cs_path,
    const uint64_t* witness_data,
    uint32_t witness_len,
    const YoimiyaSrs* srs
);

/**
 * Free a proof handle.
 */
void yoimiya_free_proof(YoimiyaProof* proof);

/* ── Verify ─────────────────────────────────────────────────────── */

/**
 * Verify a proof locally (off-chain).
 *
 * @param proof  Proof handle.
 * @param srs    SRS handle (must match the SRS used for proving).
 * @return 1 = valid, 0 = invalid, -1 = error.
 */
int32_t yoimiya_verify(
    const YoimiyaProof* proof,
    const YoimiyaSrs* srs
);

/* ── Aggregate ──────────────────────────────────────────────────── */

/**
 * Aggregate multiple proofs into a single batch proof.
 *
 * @param proofs  Array of proof handle pointers.
 * @param count   Number of proofs in the array.
 * @param srs     SRS handle.
 * @return Batch proof handle, or NULL on error. Free with yoimiya_free_batch_proof().
 */
YoimiyaBatchProof* yoimiya_aggregate(
    const YoimiyaProof* const* proofs,
    uint32_t count,
    const YoimiyaSrs* srs
);

/**
 * Free a batch proof handle.
 */
void yoimiya_free_batch_proof(YoimiyaBatchProof* batch);

/* ── Serialization ──────────────────────────────────────────────── */

/**
 * Serialize a batch proof to on-chain calldata (275 bytes).
 *
 * Compatible with YoimiyaBatchVerifier.sol.
 *
 * @param batch       Batch proof handle.
 * @param out_buf     Output buffer (must be >= 275 bytes).
 * @param out_buf_len Size of out_buf in bytes.
 * @return Number of bytes written (275), or -1 on error.
 */
int32_t yoimiya_batch_to_calldata(
    const YoimiyaBatchProof* batch,
    uint8_t* out_buf,
    uint32_t out_buf_len
);

#ifdef __cplusplus
}
#endif

#endif /* YOIMIYA_H */
