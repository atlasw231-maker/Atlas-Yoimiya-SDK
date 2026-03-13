"""
Yoimiya Test Utilities - Simple testing and validation helpers

This module provides convenient utilities for testing proofs, verifications,
and batch operations without needing to understand the internal implementation.
"""

import sys
import time
from pathlib import Path

# Add bindings to path
BINDINGS_PATH = Path(__file__).parent.parent / "bindings" / "python"
sys.path.insert(0, str(BINDINGS_PATH))

from yoimiya import generate_test_srs, prove_test, aggregate_proofs


class YoimiyaTester:
    """High-level interface for testing Yoimiya SDK functionality"""
    
    def __init__(self, max_degree=2048):
        """Initialize tester with SRS"""
        self.srs = generate_test_srs(max_degree=max_degree)
        self.max_degree = max_degree
        self.test_results = []
    
    def test_simple_proof(self, num_constraints=100, witness=None):
        """
        Test basic proof generation and verification
        
        Args:
            num_constraints: Number of circuit constraints
            witness: Optional witness data (defaults to [1,2,3,4])
        
        Returns:
            dict: Test result with timing and status
        """
        if witness is None:
            witness = [1, 2, 3, 4]
        
        result = {
            "test": "simple_proof",
            "constraints": num_constraints,
            "status": "FAILED"
        }
        
        try:
            # Measure proof generation time
            start = time.perf_counter()
            proof = prove_test(
                num_constraints=num_constraints,
                witness=witness,
                srs=self.srs
            )
            prove_time = (time.perf_counter() - start) * 1000  # Convert to ms
            
            # Measure verification time
            start = time.perf_counter()
            valid = proof.verify(self.srs)
            verify_time = (time.perf_counter() - start) * 1000
            
            result["status"] = "PASSED" if valid else "FAILED"
            result["prove_ms"] = round(prove_time, 4)
            result["verify_ms"] = round(verify_time, 4)
            result["proof_valid"] = valid
            
        except Exception as e:
            result["error"] = str(e)
        
        self.test_results.append(result)
        return result
    
    def test_batch_aggregation(self, num_proofs=5, constraints_per_proof=100, witness=None):
        """
        Test proof aggregation and batch verification
        
        Args:
            num_proofs: Number of proofs to aggregate
            constraints_per_proof: Constraints per individual proof
            witness: Optional witness data
        
        Returns:
            dict: Test result with timing and status
        """
        if witness is None:
            witness = [1, 2, 3, 4]
        
        result = {
            "test": "batch_aggregation",
            "num_proofs": num_proofs,
            "constraints_per_proof": constraints_per_proof,
            "status": "FAILED"
        }
        
        try:
            # Generate multiple proofs
            proofs = []
            for i in range(num_proofs):
                proof = prove_test(
                    num_constraints=constraints_per_proof,
                    witness=witness,
                    srs=self.srs
                )
                proofs.append(proof)
            
            # Measure aggregation time
            start = time.perf_counter()
            batch_proof = aggregate_proofs(proofs, self.srs)
            aggregate_time = (time.perf_counter() - start) * 1000
            
            # Measure batch verification time
            start = time.perf_counter()
            valid = batch_proof.verify(self.srs)
            verify_time = (time.perf_counter() - start) * 1000
            
            result["status"] = "PASSED" if valid else "FAILED"
            result["aggregate_ms"] = round(aggregate_time, 4)
            result["batch_verify_ms"] = round(verify_time, 4)
            result["batch_valid"] = valid
            
        except Exception as e:
            result["error"] = str(e)
        
        self.test_results.append(result)
        return result
    
    def test_scalability(self, constraint_sizes=None):
        """
        Test proof generation across different constraint sizes
        
        Args:
            constraint_sizes: List of constraint counts to test (default: [100, 500, 1000, 2000])
        
        Returns:
            list: Test results for each size
        """
        if constraint_sizes is None:
            constraint_sizes = [100, 500, 1000, 2000]
        
        results = []
        for size in constraint_sizes:
            result = self.test_simple_proof(num_constraints=size, witness=[1, 2, 3, 4])
            results.append(result)
        
        return results
    
    def test_large_constraints(self, constraint_sizes=None):
        """
        Test proof generation with large constraint counts (up to 1M)
        
        Useful for developers to understand performance at scale and identify
        optimal parameters for their use case.
        
        Args:
            constraint_sizes: List of large constraint counts to test
                            (default: [10K, 50K, 100K, 250K, 500K, 1M])
        
        Returns:
            list: Test results for each size
        """
        if constraint_sizes is None:
            constraint_sizes = [10_000, 50_000, 100_000, 250_000, 500_000, 1_000_000]
        
        print("\nTesting Large Constraint Sizes (up to 1M)...")
        print("-" * 60)
        
        results = []
        for size in constraint_sizes:
            print(f"  Testing {size:,} constraints...", end=" ", flush=True)
            result = self.test_simple_proof(num_constraints=size, witness=[1, 2, 3, 4])
            if result.get("status") == "PASSED":
                print(f"✓ Prove: {result.get('prove_ms')}ms, Verify: {result.get('verify_ms')}ms")
            else:
                print(f"✗ Failed: {result.get('error', 'Unknown error')}")
            results.append(result)
        
        return results
    
    def test_batch_sizes(self, batch_sizes=None, constraints_per_proof=100):
        """
        Test aggregation with different batch sizes
        
        Args:
            batch_sizes: List of batch sizes to test (default: [2, 5, 10, 20])
            constraints_per_proof: Constraints per individual proof
        
        Returns:
            list: Test results for each batch size
        """
        if batch_sizes is None:
            batch_sizes = [2, 5, 10, 20]
        
        results = []
        for batch_size in batch_sizes:
            result = self.test_batch_aggregation(
                num_proofs=batch_size,
                constraints_per_proof=constraints_per_proof
            )
            results.append(result)
        
        return results
    
    def run_full_test_suite(self):
        """
        Run comprehensive test suite covering all main operations
        
        Returns:
            dict: Summary of all tests
        """
        print("Running Yoimiya Test Suite...")
        print("=" * 60)
        
        # Test 1: Simple proofs
        print("\n[1/4] Testing simple proof generation and verification...")
        simple_results = self.test_scalability([100, 500, 1000, 2000])
        
        # Test 2: Batch aggregation
        print("[2/4] Testing batch aggregation...")
        batch_results = self.test_batch_sizes([2, 5, 10])
        
        # Test 3: Large batch
        print("[3/4] Testing large batch (100 proofs)...")
        large_batch = self.test_batch_aggregation(
            num_proofs=100,
            constraints_per_proof=100
        )
        
        # Test 4: Stress test
        print("[4/4] Testing high-constraint proof...")
        stress_test = self.test_simple_proof(num_constraints=5000, witness=[1, 2, 3, 4])
        
        # Print summary
        self._print_summary()
        
        return {
            "simple": simple_results,
            "batches": batch_results,
            "large_batch": large_batch,
            "stress": stress_test
        }
    
    def _print_summary(self):
        """Print test results summary"""
        print("\n" + "=" * 60)
        print("TEST SUMMARY")
        print("=" * 60)
        
        passed = sum(1 for r in self.test_results if r.get("status") == "PASSED")
        failed = sum(1 for r in self.test_results if r.get("status") == "FAILED")
        
        print(f"\nTotal tests: {len(self.test_results)}")
        print(f"✓ Passed: {passed}")
        print(f"✗ Failed: {failed}")
        
        print("\nDetailed Results:")
        print("-" * 60)
        for result in self.test_results:
            status = "✓" if result.get("status") == "PASSED" else "✗"
            test_name = result.get("test", "unknown")
            
            if test_name == "simple_proof":
                print(f"{status} {test_name:20} | Constraints: {result.get('constraints', 'N/A'):6} | "
                      f"Prove: {result.get('prove_ms', 'N/A')}ms | Verify: {result.get('verify_ms', 'N/A')}ms")
            elif test_name == "batch_aggregation":
                print(f"{status} {test_name:20} | Proofs: {result.get('num_proofs', 'N/A'):6} | "
                      f"Aggregate: {result.get('aggregate_ms', 'N/A')}ms | Verify: {result.get('batch_verify_ms', 'N/A')}ms")


def quick_test():
    """Quick sanity check test"""
    print("Running quick sanity check...")
    tester = YoimiyaTester(max_degree=1024)
    result = tester.test_simple_proof(num_constraints=100)
    
    if result.get("status") == "PASSED":
        print(f"✓ SDK is working! Proof generation: {result.get('prove_ms')}ms, "
              f"Verification: {result.get('verify_ms')}ms")
    else:
        print("✗ SDK test failed!")
        if "error" in result:
            print(f"Error: {result['error']}")
    
    return result


if __name__ == "__main__":
    # Run full test suite
    tester = YoimiyaTester(max_degree=2048)
    tester.run_full_test_suite()
