"""
Yoimiya Test Utilities - Simple testing and validation helpers

This module provides convenient utilities for testing proofs, verifications,
and batch operations without needing to understand the internal implementation.
"""

import ctypes
import platform
import sys
import threading
import time
from pathlib import Path

# Add bindings to path
BINDINGS_PATH = Path(__file__).parent.parent / "bindings" / "python"
sys.path.insert(0, str(BINDINGS_PATH))

from yoimiya import generate_test_srs, prove_test, aggregate_proofs


def _format_rss_mb(rss_bytes):
    if rss_bytes is None:
        return "N/A"
    return round(rss_bytes / (1024 * 1024), 2)


def _current_rss_bytes():
    system = platform.system()

    if system == "Windows":
        from ctypes import wintypes

        class PROCESS_MEMORY_COUNTERS(ctypes.Structure):
            _fields_ = [
                ("cb", wintypes.DWORD),
                ("PageFaultCount", wintypes.DWORD),
                ("PeakWorkingSetSize", ctypes.c_size_t),
                ("WorkingSetSize", ctypes.c_size_t),
                ("QuotaPeakPagedPoolUsage", ctypes.c_size_t),
                ("QuotaPagedPoolUsage", ctypes.c_size_t),
                ("QuotaPeakNonPagedPoolUsage", ctypes.c_size_t),
                ("QuotaNonPagedPoolUsage", ctypes.c_size_t),
                ("PagefileUsage", ctypes.c_size_t),
                ("PeakPagefileUsage", ctypes.c_size_t),
            ]

        counters = PROCESS_MEMORY_COUNTERS()
        counters.cb = ctypes.sizeof(PROCESS_MEMORY_COUNTERS)
        kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
        psapi = ctypes.WinDLL("psapi", use_last_error=True)
        kernel32.GetCurrentProcess.restype = wintypes.HANDLE
        psapi.GetProcessMemoryInfo.argtypes = [
            wintypes.HANDLE,
            ctypes.POINTER(PROCESS_MEMORY_COUNTERS),
            wintypes.DWORD,
        ]
        psapi.GetProcessMemoryInfo.restype = wintypes.BOOL
        process = kernel32.GetCurrentProcess()
        ok = psapi.GetProcessMemoryInfo(process, ctypes.byref(counters), counters.cb)
        if ok:
            return int(counters.WorkingSetSize)
        return None

    proc_status = Path("/proc/self/status")
    if proc_status.exists():
        for line in proc_status.read_text().splitlines():
            if line.startswith("VmRSS:"):
                parts = line.split()
                if len(parts) >= 2:
                    return int(parts[1]) * 1024

    try:
        import resource

        rss = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
        if system == "Darwin":
            return int(rss)
        return int(rss) * 1024
    except Exception:
        return None


class _PeakMemorySampler:
    def __init__(self, interval_seconds=0.01):
        self.interval_seconds = interval_seconds
        self._stop_event = threading.Event()
        self._thread = None
        self._max_rss = _current_rss_bytes()

    def start(self):
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()

    def stop(self):
        self._stop_event.set()
        if self._thread is not None:
            self._thread.join()
        current = _current_rss_bytes()
        if current is not None:
            if self._max_rss is None:
                self._max_rss = current
            else:
                self._max_rss = max(self._max_rss, current)
        return self._max_rss

    def _run(self):
        while not self._stop_event.wait(self.interval_seconds):
            current = _current_rss_bytes()
            if current is None:
                continue
            if self._max_rss is None:
                self._max_rss = current
            else:
                self._max_rss = max(self._max_rss, current)


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
            witness: Optional witness data (defaults to [1]*(num_constraints+1))
        
        Returns:
            dict: Test result with timing and status
        """
        if witness is None:
            witness = [1] * (num_constraints + 1)
        
        result = {
            "test": "simple_proof",
            "constraints": num_constraints,
            "status": "FAILED"
        }
        baseline_rss = _current_rss_bytes()
        sampler = _PeakMemorySampler()
        
        # Use a fresh SRS if the stored one is too small for this constraint count
        srs = self.srs
        if self.srs.max_degree < num_constraints + 1:
            srs = generate_test_srs(max_degree=num_constraints + 1)
        
        try:
            sampler.start()
            # Measure proof generation time
            start = time.perf_counter()
            proof = prove_test(
                num_constraints=num_constraints,
                witness=witness,
                srs=srs
            )
            prove_time = (time.perf_counter() - start) * 1000  # Convert to ms
            
            # Measure verification time
            start = time.perf_counter()
            valid = proof.verify(srs)
            verify_time = (time.perf_counter() - start) * 1000
            
            result["status"] = "PASSED" if valid else "FAILED"
            result["prove_ms"] = round(prove_time, 4)
            result["verify_ms"] = round(verify_time, 4)
            result["proof_bytes"] = proof.byte_size()
            result["proof_valid"] = valid
            
        except Exception as e:
            result["error"] = str(e)
        finally:
            peak_rss = sampler.stop()
            result["peak_rss_bytes"] = peak_rss
            result["peak_rss_mb"] = _format_rss_mb(peak_rss)
            if baseline_rss is not None and peak_rss is not None:
                result["peak_rss_delta_bytes"] = max(0, peak_rss - baseline_rss)
                result["peak_rss_delta_mb"] = _format_rss_mb(result["peak_rss_delta_bytes"])
        
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
            witness = [1] * (constraints_per_proof + 1)
        
        result = {
            "test": "batch_aggregation",
            "num_proofs": num_proofs,
            "constraints_per_proof": constraints_per_proof,
            "status": "FAILED"
        }
        baseline_rss = _current_rss_bytes()
        sampler = _PeakMemorySampler()
        
        try:
            sampler.start()
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
            result["batch_bytes"] = len(batch_proof.to_calldata())
            result["batch_valid"] = valid
            
        except Exception as e:
            result["error"] = str(e)
        finally:
            peak_rss = sampler.stop()
            result["peak_rss_bytes"] = peak_rss
            result["peak_rss_mb"] = _format_rss_mb(peak_rss)
            if baseline_rss is not None and peak_rss is not None:
                result["peak_rss_delta_bytes"] = max(0, peak_rss - baseline_rss)
                result["peak_rss_delta_mb"] = _format_rss_mb(result["peak_rss_delta_bytes"])
        
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
            result = self.test_simple_proof(num_constraints=size)
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
            # Each size needs its own SRS large enough for that constraint count
            local_srs = generate_test_srs(max_degree=size + 1)
            old_srs = self.srs
            self.srs = local_srs
            result = self.test_simple_proof(num_constraints=size)
            self.srs = old_srs
            if result.get("status") == "PASSED":
                print(
                    f"✓ Prove: {result.get('prove_ms')}ms, Verify: {result.get('verify_ms')}ms, "
                    f"Proof: {result.get('proof_bytes')} bytes, Peak RSS: {result.get('peak_rss_mb')} MB"
                )
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
        stress_test = self.test_simple_proof(num_constraints=5000)
        
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
                      f"Prove: {result.get('prove_ms', 'N/A')}ms | Verify: {result.get('verify_ms', 'N/A')}ms | "
                      f"Proof: {result.get('proof_bytes', 'N/A')} bytes | Peak RSS: {result.get('peak_rss_mb', 'N/A')} MB")
            elif test_name == "batch_aggregation":
                print(f"{status} {test_name:20} | Proofs: {result.get('num_proofs', 'N/A'):6} | "
                      f"Aggregate: {result.get('aggregate_ms', 'N/A')}ms | Verify: {result.get('batch_verify_ms', 'N/A')}ms | "
                      f"Calldata: {result.get('batch_bytes', 'N/A')} bytes | Peak RSS: {result.get('peak_rss_mb', 'N/A')} MB")


def quick_test():
    """Quick sanity check test"""
    print("Running quick sanity check...")
    tester = YoimiyaTester(max_degree=1024)
    result = tester.test_simple_proof(num_constraints=100)
    
    if result.get("status") == "PASSED":
        print(f"✓ SDK is working! Proof generation: {result.get('prove_ms')}ms, "
              f"Verification: {result.get('verify_ms')}ms, Proof: {result.get('proof_bytes')} bytes, "
              f"Peak RSS: {result.get('peak_rss_mb')} MB")
    else:
        print("✗ SDK test failed!")
        if "error" in result:
            print(f"Error: {result['error']}")
    
    return result


if __name__ == "__main__":
    # Run full test suite
    tester = YoimiyaTester(max_degree=2048)
    tester.run_full_test_suite()
