"""
Direct Proof Generation Examples

This module shows how to generate proofs directly without using test utilities.
Perfect for developers who want full control over the proof generation process.
"""

import sys
from pathlib import Path

# Add bindings to path
BINDINGS_PATH = Path(__file__).parent.parent / "bindings" / "python"
sys.path.insert(0, str(BINDINGS_PATH))

from yoimiya import generate_test_srs, prove_test, aggregate_proofs


def example_basic_proof():
    """Generate a simple proof and verify it"""
    print("=" * 60)
    print("Example 1: Basic Proof Generation")
    print("=" * 60)
    
    # Generate SRS once (reuse for multiple proofs)
    srs = generate_test_srs(max_degree=2048)
    print("✓ Generated SRS with max degree 2048")
    
    # Generate a proof (witness is auto-padded for test circuits)
    num_constraints = 500
    proof = prove_test(
        num_constraints=num_constraints,
        srs=srs
    )
    print(f"✓ Generated proof for {num_constraints} constraints")
    
    # Verify the proof
    is_valid = proof.verify(srs)
    print(f"✓ Proof verification: {'PASSED' if is_valid else 'FAILED'}")
    
    return srs, proof


def example_large_proof():
    """Generate a proof with large constraint count"""
    print("\n" + "=" * 60)
    print("Example 2: Large Constraint Proof (1M)")
    print("=" * 60)
    
    # Create larger SRS for big proofs
    print("Generating large SRS...")
    srs = generate_test_srs(max_degree=1_000_000)
    print("✓ Generated SRS with max degree 1M")
    
    # Generate large proof (witness auto-padded)
    print("Generating proof for 1,000,000 constraints...")
    proof = prove_test(
        num_constraints=1_000_000,
        srs=srs
    )
    print("✓ Generated proof")
    
    # Verify
    is_valid = proof.verify(srs)
    print(f"✓ Proof verification: {'PASSED' if is_valid else 'FAILED'}")
    
    return proof


def example_batch_aggregation():
    """Generate multiple proofs and aggregate them"""
    print("\n" + "=" * 60)
    print("Example 3: Batch Proof Aggregation")
    print("=" * 60)
    
    # Setup
    srs = generate_test_srs(max_degree=2048)
    print("✓ Generated SRS")
    
    # Generate multiple proofs
    num_proofs = 5
    proofs = []
    
    print(f"Generating {num_proofs} proofs...")
    for i in range(num_proofs):
        proof = prove_test(
            num_constraints=1000,
            srs=srs
        )
        proofs.append(proof)
        print(f"  ✓ Generated proof {i+1}/{num_proofs}")
    
    # Aggregate proofs
    print(f"Aggregating {num_proofs} proofs...")
    batch_proof = aggregate_proofs(proofs, srs)
    print("✓ Aggregation complete")
    
    # Verify batch
    is_valid = batch_proof.verify(srs)
    print(f"✓ Batch verification: {'PASSED' if is_valid else 'FAILED'}")
    
    return batch_proof


def example_custom_witness():
    """Generate proofs with custom witness data"""
    print("\n" + "=" * 60)
    print("Example 4: Custom Witness Data")
    print("=" * 60)
    
    srs = generate_test_srs(max_degree=2048)
    
    # Example 1: Simple witness (auto-padded to required size)
    witness1 = [1, 2, 3, 4]
    proof1 = prove_test(100, witness1, srs)
    print(f"✓ Proof with seed witness {witness1}: {proof1.verify(srs)}")
    
    # Example 2: Larger witness
    witness2 = [10, 20, 30, 40, 50, 60, 70, 80]
    proof2 = prove_test(500, witness2, srs)
    print(f"✓ Proof with seed witness {witness2}: {proof2.verify(srs)}")
    
    # Example 3: No witness (fully auto-generated)
    proof3 = prove_test(1000, srs=srs)
    print(f"✓ Proof with default witness: {proof3.verify(srs)}")


def example_performance_tracking():
    """Track performance metrics for your use case"""
    print("\n" + "=" * 60)
    print("Example 5: Performance Tracking")
    print("=" * 60)
    
    import time
    
    srs = generate_test_srs(max_degree=1_000_000)
    print("✓ Generated SRS")
    
    test_sizes = [100_000, 500_000, 1_000_000]
    results = {}
    
    for size in test_sizes:
        print(f"\nTesting {size:,} constraints...")
        
        # Measure proof generation
        start = time.perf_counter()
        proof = prove_test(size, srs=srs)
        prove_time = (time.perf_counter() - start) * 1000
        
        # Measure verification
        start = time.perf_counter()
        valid = proof.verify(srs)
        verify_time = (time.perf_counter() - start) * 1000
        
        results[size] = {
            'prove_ms': prove_time,
            'verify_ms': verify_time,
            'valid': valid
        }
        
        print(f"  Prove: {prove_time:.4f} ms")
        print(f"  Verify: {verify_time:.4f} ms")
        print(f"  Valid: {valid}")
    
    # Print summary
    print("\n" + "-" * 60)
    print("Performance Summary:")
    print("-" * 60)
    for size, metrics in results.items():
        print(f"{size:,} constraints: "
              f"Prove {metrics['prove_ms']:.4f}ms | "
              f"Verify {metrics['verify_ms']:.4f}ms")


def example_production_workflow():
    """Recommended workflow for production use"""
    print("\n" + "=" * 60)
    print("Example 6: Production Workflow")
    print("=" * 60)
    
    print("""
    Step 1: Initialize SRS (do once, reuse)
    -------
    srs = generate_test_srs(max_degree=YOUR_MAX_CONSTRAINT_COUNT)
    
    Step 2: For each computation to prove:
    -------
    proof = prove_test(
        num_constraints=YOUR_CONSTRAINT_COUNT,
        witness=YOUR_WITNESS_DATA,
        srs=srs
    )
    
    Step 3: Verify locally (optional for dev/testing)
    -------
    is_valid = proof.verify(srs)
    
    Step 4: Batch multiple proofs if needed
    -------
    batch_proof = aggregate_proofs([proof1, proof2, ...], srs)
    
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
    """)


if __name__ == "__main__":
    # Run all examples
    example_basic_proof()
    example_large_proof()
    example_batch_aggregation()
    example_custom_witness()
    example_performance_tracking()
    example_production_workflow()
    
    print("\n" + "=" * 60)
    print("✓ All examples completed!")
    print("=" * 60)
