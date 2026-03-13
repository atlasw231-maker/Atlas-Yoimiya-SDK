/**
 * Direct Proof Generation Examples
 * 
 * This file shows how to generate proofs directly without using test utilities.
 * Perfect for developers who want full control over the proof generation process.
 */

const { generateTestSrs, proveTest, aggregateProofs } = require('../bindings/nodejs');


async function exampleBasicProof() {
    console.log('='.repeat(60));
    console.log('Example 1: Basic Proof Generation');
    console.log('='.repeat(60));
    
    // Generate SRS once (reuse for multiple proofs)
    const srs = generateTestSrs(2048);
    console.log('✓ Generated SRS with max degree 2048');
    
    // Generate a proof
    const witness = [1n, 2n, 3n, 4n];
    const numConstraints = 500;
    const proof = proveTest(numConstraints, witness, srs);
    console.log(`✓ Generated proof for ${numConstraints} constraints`);
    
    // Verify the proof
    const isValid = proof.verify(srs);
    console.log(`✓ Proof verification: ${isValid ? 'PASSED' : 'FAILED'}`);
    
    return { srs, proof };
}

async function exampleLargeProof() {
    console.log('\n' + '='.repeat(60));
    console.log('Example 2: Large Constraint Proof (1M)');
    console.log('='.repeat(60));
    
    // Create larger SRS for big proofs
    console.log('Generating large SRS...');
    const srs = generateTestSrs(1_000_000);
    console.log('✓ Generated SRS with max degree 1M');
    
    // Generate large proof
    console.log('Generating proof for 1,000,000 constraints...');
    const witness = [1n, 2n, 3n, 4n];
    const proof = proveTest(1_000_000, witness, srs);
    console.log('✓ Generated proof');
    
    // Verify
    const isValid = proof.verify(srs);
    console.log(`✓ Proof verification: ${isValid ? 'PASSED' : 'FAILED'}`);
    
    return proof;
}

async function exampleBatchAggregation() {
    console.log('\n' + '='.repeat(60));
    console.log('Example 3: Batch Proof Aggregation');
    console.log('='.repeat(60));
    
    // Setup
    const srs = generateTestSrs(2048);
    console.log('✓ Generated SRS');
    
    // Generate multiple proofs
    const numProofs = 5;
    const proofs = [];
    const witness = [1n, 2n, 3n, 4n];
    
    console.log(`Generating ${numProofs} proofs...`);
    for (let i = 0; i < numProofs; i++) {
        const proof = proveTest(1000, witness, srs);
        proofs.push(proof);
        console.log(`  ✓ Generated proof ${i + 1}/${numProofs}`);
    }
    
    // Aggregate proofs
    console.log(`Aggregating ${numProofs} proofs...`);
    const batchProof = aggregateProofs(proofs, srs);
    console.log('✓ Aggregation complete');
    
    // Verify batch
    const isValid = batchProof.verify(srs);
    console.log(`✓ Batch verification: ${isValid ? 'PASSED' : 'FAILED'}`);
    
    return batchProof;
}

async function exampleCustomWitness() {
    console.log('\n' + '='.repeat(60));
    console.log('Example 4: Custom Witness Data');
    console.log('='.repeat(60));
    
    const srs = generateTestSrs(2048);
    
    // Example 1: Simple witness
    const witness1 = [1n, 2n, 3n, 4n];
    const proof1 = proveTest(100, witness1, srs);
    console.log(`✓ Proof with witness [1,2,3,4]: ${proof1.verify(srs)}`);
    
    // Example 2: Larger witness
    const witness2 = [10n, 20n, 30n, 40n, 50n, 60n, 70n, 80n];
    const proof2 = proveTest(500, witness2, srs);
    console.log(`✓ Proof with witness [10,20,...,80]: ${proof2.verify(srs)}`);
    
    // Example 3: Real-world example (transaction data)
    const witness3 = [0xDEADBEEFn, 0xCAFEBABEn, 0x12345678n, 0xABCDEF00n];
    const proof3 = proveTest(1000, witness3, srs);
    console.log(`✓ Proof with witness [0xDEADBEEF, ...]: ${proof3.verify(srs)}`);
}

async function examplePerformanceTracking() {
    console.log('\n' + '='.repeat(60));
    console.log('Example 5: Performance Tracking');
    console.log('='.repeat(60));
    
    const srs = generateTestSrs(1_000_000);
    console.log('✓ Generated SRS');
    
    const testSizes = [100_000, 500_000, 1_000_000];
    const results = {};
    
    for (const size of testSizes) {
        console.log(`\nTesting ${size.toLocaleString()} constraints...`);
        
        // Measure proof generation
        let start = process.hrtime.bigint();
        const proof = proveTest(size, [1n, 2n, 3n, 4n], srs);
        const proveTime = Number(process.hrtime.bigint() - start) / 1_000_000;
        
        // Measure verification
        start = process.hrtime.bigint();
        const valid = proof.verify(srs);
        const verifyTime = Number(process.hrtime.bigint() - start) / 1_000_000;
        
        results[size] = {
            prove_ms: proveTime,
            verify_ms: verifyTime,
            valid: valid
        };
        
        console.log(`  Prove: ${proveTime.toFixed(4)} ms`);
        console.log(`  Verify: ${verifyTime.toFixed(4)} ms`);
        console.log(`  Valid: ${valid}`);
    }
    
    // Print summary
    console.log('\n' + '-'.repeat(60));
    console.log('Performance Summary:');
    console.log('-'.repeat(60));
    for (const [size, metrics] of Object.entries(results)) {
        console.log(`${parseInt(size).toLocaleString()} constraints: ` +
            `Prove ${metrics.prove_ms.toFixed(4)}ms | ` +
            `Verify ${metrics.verify_ms.toFixed(4)}ms`);
    }
}

async function exampleProductionWorkflow() {
    console.log('\n' + '='.repeat(60));
    console.log('Example 6: Production Workflow');
    console.log('='.repeat(60));
    
    console.log(`
    Step 1: Initialize SRS (do once, reuse)
    -------
    const srs = generateTestSrs(YOUR_MAX_CONSTRAINT_COUNT);
    
    Step 2: For each computation to prove:
    -------
    const proof = proveTest(
        YOUR_CONSTRAINT_COUNT,
        YOUR_WITNESS_DATA,
        srs
    );
    
    Step 3: Verify locally (optional for dev/testing)
    -------
    const isValid = proof.verify(srs);
    
    Step 4: Batch multiple proofs if needed
    -------
    const batchProof = aggregateProofs([proof1, proof2, ...], srs);
    
    Step 5: Use proof/batch_proof in your application
    -------
    - Send to smart contract for on-chain verification
    - Store in database
    - Return to client
    - Pass to another service
    
    Best Practices:
    - Reuse SRS for multiple proofs
    - Generate SRS with max degree >= your largest constraint count
    - Batch proofs if you have multiple to aggregate
    - Cache verification keys if possible
    - Monitor proof generation times
    `);
}

async function runAllExamples() {
    try {
        await exampleBasicProof();
        await exampleLargeProof();
        await exampleBatchAggregation();
        await exampleCustomWitness();
        await examplePerformanceTracking();
        await exampleProductionWorkflow();
        
        console.log('\n' + '='.repeat(60));
        console.log('✓ All examples completed!');
        console.log('='.repeat(60));
    } catch (error) {
        console.error('Error running examples:', error);
    }
}

// Run examples
runAllExamples();

module.exports = {
    exampleBasicProof,
    exampleLargeProof,
    exampleBatchAggregation,
    exampleCustomWitness,
    examplePerformanceTracking,
    exampleProductionWorkflow
};
