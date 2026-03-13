#!/usr/bin/env python3
"""
Yoimiya ZK Proving SDK - Python Example

This example demonstrates:
1. Generating SRS
2. Creating a witness
3. Proving a circuit
4. Verifying the proof
5. Aggregating multiple proofs
6. Verifying the batch proof
"""

import time
import random
import sys
from pathlib import Path

# Add SDK to path
sdk_path = Path(__file__).parent.parent / "bindings" / "python"
sys.path.insert(0, str(sdk_path))

from yoimiya import (
    generate_test_srs,
    prove_test,
    aggregate_proofs,
)

def main():
    print("=== Yoimiya ZK Proving SDK - Python Example ===\n")
    
    # Step 1: Generate SRS
    print("Step 1: Generating SRS (max_degree=2048)...")
    srs = generate_test_srs(max_degree=2048)
    print("  ✓ SRS generated successfully\n")
    
    # Step 2: Create witness
    print("Step 2: Creating witness...")
    witness = [random.randint(0, 1000) for _ in range(100)]
    print(f"  ✓ Witness created ({len(witness)} elements)\n")
    
    # Step 3: Prove
    print("Step 3: Proving circuit (constraints=500)...")
    start = time.time()
    
    proof = prove_test(
        num_constraints=500,
        witness=witness,
        srs=srs
    )
    
    elapsed = (time.time() - start) * 1000
    print(f"  ✓ Proof generated in {elapsed:.2f} ms\n")
    
    # Step 4: Verify single proof
    print("Step 4: Verifying proof...")
    try:
        is_valid = proof.verify(srs)
        if is_valid:
            print("  ✓ Proof is VALID\n")
        else:
            print("  ✗ Proof is INVALID\n")
    except Exception as e:
        print(f"  ✗ Verification error: {e}\n")
        return 1
    
    # Step 5: Generate multiple proofs for aggregation
    print("Step 5: Generating multiple proofs for aggregation...")
    proofs = [proof]
    for i in range(1, 3):
        try:
            p = prove_test(num_constraints=500, witness=witness, srs=srs)
            proofs.append(p)
        except Exception as e:
            print(f"  ✗ Failed to generate proof {i+1}: {e}")
            return 1
    print(f"  ✓ Generated {len(proofs)} proofs\n")
    
    # Step 6: Aggregate proofs
    print("Step 6: Aggregating proofs...")
    try:
        batch_proof = aggregate_proofs(proofs, srs)
        print(f"  ✓ Aggregated {len(proofs)} proofs\n")
    except Exception as e:
        print(f"  ✗ Aggregation error: {e}\n")
        return 1
    
    # Step 7: Verify batch proof
    print("Step 7: Verifying batch proof...")
    try:
        is_batch_valid = batch_proof.verify(srs)
        if is_batch_valid:
            print("  ✓ Batch proof is VALID\n")
        else:
            print("  ✗ Batch proof is INVALID\n")
    except Exception as e:
        print(f"  ✗ Batch verification error: {e}\n")
        return 1
    
    print("Done!")
    return 0

if __name__ == "__main__":
    sys.exit(main())
