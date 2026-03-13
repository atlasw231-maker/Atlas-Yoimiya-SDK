#include <yoimiya.h>
#include <stdio.h>
#include <stdint.h>
#include <stdlib.h>
#include <time.h>

int main(int argc, char* argv[]) {
    printf("=== Yoimiya ZK Proving SDK - C Example ===\n\n");
    
    // Initialize random seed
    srand(time(NULL));
    
    // Step 1: Generate SRS
    printf("Step 1: Generating SRS (max_degree=2048)...\n");
    YoimiyaSrs* srs = yoimiya_generate_test_srs(2048);
    if (!srs) {
        fprintf(stderr, "ERROR: Failed to generate SRS\n");
        return 1;
    }
    printf("  ✓ SRS generated successfully\n\n");
    
    // Step 2: Create witness
    printf("Step 2: Creating witness...\n");
    uint32_t witness_len = 100;
    uint64_t* witness = (uint64_t*)malloc(witness_len * sizeof(uint64_t));
    if (!witness) {
        fprintf(stderr, "ERROR: Memory allocation failed\n");
        yoimiya_free_srs(srs);
        return 1;
    }
    
    for (uint32_t i = 0; i < witness_len; i++) {
        witness[i] = (uint64_t)(rand() % 1000);
    }
    printf("  ✓ Witness created (%u elements)\n\n", witness_len);
    
    // Step 3: Prove
    printf("Step 3: Proving circuit (constraints=500)...\n");
    clock_t start = clock();
    
    YoimiyaProof* proof = yoimiya_prove_test(
        500,           // num_constraints
        witness,       // witness data
        witness_len,   // witness length
        srs            // SRS
    );
    
    clock_t end = clock();
    double elapsed = ((double)(end - start)) / CLOCKS_PER_SEC * 1000;
    
    if (!proof) {
        fprintf(stderr, "ERROR: Proving failed\n");
        free(witness);
        yoimiya_free_srs(srs);
        return 1;
    }
    printf("  ✓ Proof generated in %.2f ms\n\n", elapsed);
    
    // Step 4: Verify single proof
    printf("Step 4: Verifying proof...\n");
    int32_t verify_result = yoimiya_verify(proof, srs);
    
    if (verify_result == -1) {
        fprintf(stderr, "ERROR: Verification error\n");
        yoimiya_free_proof(proof);
        free(witness);
        yoimiya_free_srs(srs);
        return 1;
    } else if (verify_result == 1) {
        printf("  ✓ Proof is VALID\n\n");
    } else {
        printf("  ✗ Proof is INVALID\n\n");
    }
    
    // Step 5: Generate multiple proofs for aggregation
    printf("Step 5: Generating multiple proofs for aggregation...\n");
    uint32_t num_proofs = 3;
    YoimiyaProof** proofs = (YoimiyaProof**)malloc(num_proofs * sizeof(YoimiyaProof*));
    
    proofs[0] = proof;
    for (uint32_t i = 1; i < num_proofs; i++) {
        proofs[i] = yoimiya_prove_test(500, witness, witness_len, srs);
        if (!proofs[i]) {
            fprintf(stderr, "ERROR: Failed to generate proof %u\n", i + 1);
            goto cleanup;
        }
    }
    printf("  ✓ Generated %u proofs\n\n", num_proofs);
    
    // Step 6: Aggregate proofs
    printf("Step 6: Aggregating proofs...\n");
    YoimiyaBatchProof* batch_proof = yoimiya_aggregate(
        proofs,
        num_proofs,
        srs
    );
    
    if (!batch_proof) {
        fprintf(stderr, "ERROR: Aggregation failed\n");
        goto cleanup;
    }
    printf("  ✓ Aggregated %u proofs\n\n", num_proofs);
    
    // Step 7: Verify batch proof
    printf("Step 7: Verifying batch proof...\n");
    int32_t batch_verify_result = yoimiya_verify_batch(batch_proof, srs);
    
    if (batch_verify_result == -1) {
        fprintf(stderr, "ERROR: Batch verification error\n");
    } else if (batch_verify_result == 1) {
        printf("  ✓ Batch proof is VALID\n\n");
    } else {
        printf("  ✗ Batch proof is INVALID\n\n");
    }
    
    // Cleanup
cleanup:
    if (batch_proof) yoimiya_free_batch_proof(batch_proof);
    for (uint32_t i = 1; i < num_proofs; i++) {
        if (proofs[i]) yoimiya_free_proof(proofs[i]);
    }
    free(proofs);
    yoimiya_free_proof(proof);
    free(witness);
    yoimiya_free_srs(srs);
    
    printf("Done!\n");
    return 0;
}
