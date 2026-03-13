#ifndef YOIMIYA_TEST_UTILS_H
#define YOIMIYA_TEST_UTILS_H

#include "yoimiya.h"
#include <stdint.h>
#include <time.h>

#ifdef __cplusplus
extern "C" {
#endif

/**
 * @brief Test result structure
 */
typedef struct {
    char test_name[32];       // "simple_proof" or "batch_aggregation"
    char status[16];          // "PASSED" or "FAILED"
    int32_t num_constraints;
    int32_t num_proofs;
    double prove_ms;
    double verify_ms;
    double aggregate_ms;
    double batch_verify_ms;
    int valid;
    char error[256];
} YoimiyaTestResult;

/**
 * @brief Get current time in milliseconds
 */
static inline double yoimiya_time_ms(void) {
    struct timespec ts;
    clock_gettime(CLOCK_MONOTONIC, &ts);
    return ts.tv_sec * 1000.0 + ts.tv_nsec / 1000000.0;
}

/**
 * @brief Test basic proof generation and verification
 * 
 * @param num_constraints Number of circuit constraints
 * @param witness Witness data (array of bytes)
 * @param witness_len Length of witness data
 * @param srs Structured Reference String
 * @param result Output test result
 * @return 0 on success, -1 on failure
 */
int yoimiya_test_simple_proof(
    int32_t num_constraints,
    const uint8_t* witness,
    int witness_len,
    YoimiyaSrs* srs,
    YoimiyaTestResult* result
);

/**
 * @brief Test proof aggregation and batch verification
 * 
 * @param num_proofs Number of proofs to aggregate
 * @param constraints_per_proof Constraints per individual proof
 * @param witness Witness data
 * @param witness_len Length of witness data
 * @param srs Structured Reference String
 * @param result Output test result
 * @return 0 on success, -1 on failure
 */
int yoimiya_test_batch_aggregation(
    int32_t num_proofs,
    int32_t constraints_per_proof,
    const uint8_t* witness,
    int witness_len,
    YoimiyaSrs* srs,
    YoimiyaTestResult* result
);

/**
 * @brief Test scalability across different constraint sizes
 * 
 * @param srs Structured Reference String
 * @param results Output array for results
 * @param num_tests Number of tests to run
 * @return Number of tests completed
 */
int yoimiya_test_scalability(
    YoimiyaSrs* srs,
    YoimiyaTestResult* results,
    int num_tests
);

/**
 * @brief Test batch aggregation with different batch sizes
 * 
 * @param srs Structured Reference String
 * @param results Output array for results
 * @param num_tests Number of tests to run
 * @return Number of tests completed
 */
int yoimiya_test_batch_sizes(
    YoimiyaSrs* srs,
    YoimiyaTestResult* results,
    int num_tests
);

/**
 * @brief Print test result to stdout
 */
void yoimiya_print_result(const YoimiyaTestResult* result);

/**
 * @brief Print summary of multiple test results
 */
void yoimiya_print_summary(
    const YoimiyaTestResult* results,
    int num_results
);

/**
 * @brief Quick sanity check
 * 
 * @return 1 if SDK is working, 0 otherwise
 */
int yoimiya_quick_test(void);


/* Implementation stubs - developers implement based on their needs */

/**
 * Helper: Create default witness data
 */
static inline uint8_t* yoimiya_default_witness(int* len) {
    static uint8_t witness[4] = { 1, 2, 3, 4 };
    *len = 4;
    return witness;
}

/**
 * Helper: Format time result string
 */
static inline void yoimiya_format_time(double ms, char* buffer, int size) {
    snprintf(buffer, size, "%.4f", ms);
}


#ifdef __cplusplus
}
#endif

#endif /* YOIMIYA_TEST_UTILS_H */
