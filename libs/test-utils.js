/**
 * Yoimiya Test Utilities - Simple testing and validation helpers
 * 
 * This module provides convenient utilities for testing proofs, verifications,
 * and batch operations without needing to understand the internal implementation.
 */

const { generateTestSrs, proveTest, aggregateProofs } = require('../bindings/nodejs');


class YoimiyaTester {
    /**
     * Initialize tester with SRS
     * @param {number} maxDegree - Maximum polynomial degree
     */
    constructor(maxDegree = 2048) {
        this.srs = generateTestSrs(maxDegree);
        this.maxDegree = maxDegree;
        this.testResults = [];
    }

    /**
     * Test basic proof generation and verification
     * @param {number} numConstraints - Number of circuit constraints
     * @param {Array<bigint>} witness - Optional witness data
     * @returns {Object} Test result with timing and status
     */
    testSimpleProof(numConstraints = 100, witness = null) {
        if (!witness) {
            witness = [1n, 2n, 3n, 4n];
        }

        const result = {
            test: 'simple_proof',
            constraints: numConstraints,
            status: 'FAILED'
        };

        try {
            // Measure proof generation time
            let start = process.hrtime.bigint();
            const proof = proveTest(numConstraints, witness, this.srs);
            const proveTime = Number(process.hrtime.bigint() - start) / 1_000_000; // Convert to ms

            // Measure verification time
            start = process.hrtime.bigint();
            const valid = proof.verify(this.srs);
            const verifyTime = Number(process.hrtime.bigint() - start) / 1_000_000;

            result.status = valid ? 'PASSED' : 'FAILED';
            result.prove_ms = Math.round(proveTime * 10000) / 10000;
            result.verify_ms = Math.round(verifyTime * 10000) / 10000;
            result.proof_valid = valid;

        } catch (error) {
            result.error = error.message;
        }

        this.testResults.push(result);
        return result;
    }

    /**
     * Test proof aggregation and batch verification
     * @param {number} numProofs - Number of proofs to aggregate
     * @param {number} constraintsPerProof - Constraints per individual proof
     * @param {Array<bigint>} witness - Optional witness data
     * @returns {Object} Test result with timing and status
     */
    testBatchAggregation(numProofs = 5, constraintsPerProof = 100, witness = null) {
        if (!witness) {
            witness = [1n, 2n, 3n, 4n];
        }

        const result = {
            test: 'batch_aggregation',
            num_proofs: numProofs,
            constraints_per_proof: constraintsPerProof,
            status: 'FAILED'
        };

        try {
            // Generate multiple proofs
            const proofs = [];
            for (let i = 0; i < numProofs; i++) {
                const proof = proveTest(constraintsPerProof, witness, this.srs);
                proofs.push(proof);
            }

            // Measure aggregation time
            let start = process.hrtime.bigint();
            const batchProof = aggregateProofs(proofs, this.srs);
            const aggregateTime = Number(process.hrtime.bigint() - start) / 1_000_000;

            // Measure batch verification time
            start = process.hrtime.bigint();
            const valid = batchProof.verify(this.srs);
            const verifyTime = Number(process.hrtime.bigint() - start) / 1_000_000;

            result.status = valid ? 'PASSED' : 'FAILED';
            result.aggregate_ms = Math.round(aggregateTime * 10000) / 10000;
            result.batch_verify_ms = Math.round(verifyTime * 10000) / 10000;
            result.batch_valid = valid;

        } catch (error) {
            result.error = error.message;
        }

        this.testResults.push(result);
        return result;
    }

    /**
     * Test proof generation across different constraint sizes
     * @param {Array<number>} constraintSizes - List of constraint counts to test
     * @returns {Array<Object>} Test results for each size
     */
    testScalability(constraintSizes = null) {
        if (!constraintSizes) {
            constraintSizes = [100, 500, 1000, 2000];
        }

        const results = [];
        for (const size of constraintSizes) {
            const result = this.testSimpleProof(size, [1n, 2n, 3n, 4n]);
            results.push(result);
        }

        return results;
    }

    /**
     * Test aggregation with different batch sizes
     * @param {Array<number>} batchSizes - List of batch sizes to test
     * @param {number} constraintsPerProof - Constraints per individual proof
     * @returns {Array<Object>} Test results for each batch size
     */
    testBatchSizes(batchSizes = null, constraintsPerProof = 100) {
        if (!batchSizes) {
            batchSizes = [2, 5, 10, 20];
        }

        const results = [];
        for (const batchSize of batchSizes) {
            const result = this.testBatchAggregation(batchSize, constraintsPerProof);
            results.push(result);
        }

        return results;
    }

    /**
     * Run comprehensive test suite
     * @returns {Object} Summary of all tests
     */
    async runFullTestSuite() {
        console.log('Running Yoimiya Test Suite...');
        console.log('='.repeat(60));

        // Test 1: Simple proofs
        console.log('\n[1/4] Testing simple proof generation and verification...');
        const simpleResults = this.testScalability([100, 500, 1000, 2000]);

        // Test 2: Batch aggregation
        console.log('[2/4] Testing batch aggregation...');
        const batchResults = this.testBatchSizes([2, 5, 10]);

        // Test 3: Large batch
        console.log('[3/4] Testing large batch (100 proofs)...');
        const largeBatch = this.testBatchAggregation(100, 100);

        // Test 4: Stress test
        console.log('[4/4] Testing high-constraint proof...');
        const stressTest = this.testSimpleProof(5000, [1n, 2n, 3n, 4n]);

        // Print summary
        this._printSummary();

        return {
            simple: simpleResults,
            batches: batchResults,
            large_batch: largeBatch,
            stress: stressTest
        };
    }

    /**
     * Print test results summary
     * @private
     */
    _printSummary() {
        console.log('\n' + '='.repeat(60));
        console.log('TEST SUMMARY');
        console.log('='.repeat(60));

        const passed = this.testResults.filter(r => r.status === 'PASSED').length;
        const failed = this.testResults.filter(r => r.status === 'FAILED').length;

        console.log(`\nTotal tests: ${this.testResults.length}`);
        console.log(`✓ Passed: ${passed}`);
        console.log(`✗ Failed: ${failed}`);

        console.log('\nDetailed Results:');
        console.log('-'.repeat(60));
        for (const result of this.testResults) {
            const status = result.status === 'PASSED' ? '✓' : '✗';
            const testName = result.test || 'unknown';

            if (testName === 'simple_proof') {
                console.log(`${status} ${testName.padEnd(20)} | Constraints: ${String(result.constraints).padEnd(6)} | ` +
                    `Prove: ${result.prove_ms}ms | Verify: ${result.verify_ms}ms`);
            } else if (testName === 'batch_aggregation') {
                console.log(`${status} ${testName.padEnd(20)} | Proofs: ${String(result.num_proofs).padEnd(6)} | ` +
                    `Aggregate: ${result.aggregate_ms}ms | Verify: ${result.batch_verify_ms}ms`);
            }
        }
    }
}

/**
 * Quick sanity check test
 */
async function quickTest() {
    console.log('Running quick sanity check...');
    const tester = new YoimiyaTester(1024);
    const result = tester.testSimpleProof(100);

    if (result.status === 'PASSED') {
        console.log(`✓ SDK is working! Proof generation: ${result.prove_ms}ms, ` +
            `Verification: ${result.verify_ms}ms`);
    } else {
        console.log('✗ SDK test failed!');
        if (result.error) {
            console.log(`Error: ${result.error}`);
        }
    }

    return result;
}

module.exports = {
    YoimiyaTester,
    quickTest
};
