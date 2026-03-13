#!/usr/bin/env node

/**
 * Yoimiya ZK Proving SDK - Node.js Example
 *
 * This example demonstrates:
 * 1. Generating SRS
 * 2. Creating a witness
 * 3. Proving a circuit
 * 4. Verifying the proof
 * 5. Aggregating multiple proofs
 * 6. Verifying the batch proof
 */

const {
  generateTestSrs,
  proveTest,
  aggregateProofs,
} = require('../bindings/nodejs');

async function main() {
  console.log('=== Yoimiya ZK Proving SDK - Node.js Example ===\n');
  
  try {
    // Step 1: Generate SRS
    console.log('Step 1: Generating SRS (max_degree=2048)...');
    const srs = generateTestSrs(2048);
    console.log('  ✓ SRS generated successfully\n');
    
    // Step 2: Create witness
    console.log('Step 2: Creating witness...');
    const witness = [];
    for (let i = 0; i < 100; i++) {
      witness.push(Math.floor(Math.random() * 1000));
    }
    console.log(`  ✓ Witness created (${witness.length} elements)\n`);
    
    // Step 3: Prove
    console.log('Step 3: Proving circuit (constraints=500)...');
    const startProve = Date.now();
    
    const proof = proveTest(500, witness, srs);
    
    const elapsedProve = Date.now() - startProve;
    console.log(`  ✓ Proof generated in ${elapsedProve.toFixed(2)} ms\n`);
    
    // Step 4: Verify single proof
    console.log('Step 4: Verifying proof...');
    try {
      const isValid = proof.verify(srs);
      if (isValid) {
        console.log('  ✓ Proof is VALID\n');
      } else {
        console.log('  ✗ Proof is INVALID\n');
      }
    } catch (err) {
      console.error(`  ✗ Verification error: ${err.message}\n`);
      return 1;
    }
    
    // Step 5: Generate multiple proofs for aggregation
    console.log('Step 5: Generating multiple proofs for aggregation...');
    const proofs = [proof];
    
    for (let i = 1; i < 3; i++) {
      try {
        const p = proveTest(500, witness, srs);
        proofs.push(p);
      } catch (err) {
        console.error(`  ✗ Failed to generate proof ${i + 1}: ${err.message}`);
        return 1;
      }
    }
    console.log(`  ✓ Generated ${proofs.length} proofs\n`);
    
    // Step 6: Aggregate proofs
    console.log('Step 6: Aggregating proofs...');
    try {
      const startAggregate = Date.now();
      const batchProof = aggregateProofs(proofs, srs);
      const elapsedAggregate = Date.now() - startAggregate;
      
      console.log(`  ✓ Aggregated ${proofs.length} proofs in ${elapsedAggregate.toFixed(2)} ms\n`);
      
      // Step 7: Verify batch proof
      console.log('Step 7: Verifying batch proof...');
      try {
        const isBatchValid = batchProof.verify(srs);
        if (isBatchValid) {
          console.log('  ✓ Batch proof is VALID\n');
        } else {
          console.log('  ✗ Batch proof is INVALID\n');
        }
      } catch (err) {
        console.error(`  ✗ Batch verification error: ${err.message}\n`);
        return 1;
      }
      
      // Cleanup
      proofs.forEach(p => p.destroy());
      batchProof.destroy();
    } catch (err) {
      console.error(`  ✗ Aggregation error: ${err.message}\n`);
      return 1;
    }
    
    srs.destroy();
    console.log('Done!');
    return 0;
    
  } catch (err) {
    console.error(`ERROR: ${err.message}`);
    return 1;
  }
}

main().then(code => process.exit(code));
