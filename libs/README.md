# Test Utilities Library

High-level testing utilities for the Yoimiya SDK that make it easy to test proofs, batch operations, and performance characteristics without understanding the internal implementation.

## Overview

The test utilities provide:

- **Simple Proof Testing** - Generate and verify individual proofs with prove time, verify time, proof size, and peak RSS telemetry
- **Batch Aggregation Testing** - Test proof aggregation and batch verification with aggregation time, calldata size, and peak RSS telemetry
- **Scalability Testing** - Benchmark proof generation across different constraint sizes
- **Batch Size Testing** - Evaluate performance with different batch sizes
- **Comprehensive Test Suite** - Run full test coverage in one call
- **Quick Sanity Check** - Verify SDK is working correctly

## Available Implementations

### Python: `test-utils.py`

```python
from libs.test_utils import YoimiyaTester, quick_test

# Quick check
quick_test()

# Comprehensive testing
tester = YoimiyaTester(max_degree=2048)
results = tester.run_full_test_suite()

# Individual tests
result = tester.test_simple_proof(num_constraints=500)
batch = tester.test_batch_aggregation(num_proofs=10)
scalability = tester.test_scalability([100, 500, 1000, 2000])
```

### Node.js: `test-utils.js`

```javascript
const { YoimiyaTester, quickTest } = require('./libs/test-utils.js');

// Quick check
await quickTest();

// Comprehensive testing
const tester = new YoimiyaTester(2048);
const results = await tester.runFullTestSuite();

// Individual tests
const result = tester.testSimpleProof(500);
const batch = tester.testBatchAggregation(10);
const scalability = tester.testScalability([100, 500, 1000, 2000]);
```

### C#: `test-utils.cs`

```csharp
using Yoimiya.TestUtils;

// Quick check
QuickTest.Run();

// Comprehensive testing
var tester = new YoimiyaTester(2048);
var results = tester.RunFullTestSuite();

// Individual tests
var result = tester.TestSimpleProof(500);
var batch = tester.TestBatchAggregation(10);
var scalability = tester.TestScalability(new[] { 100, 500, 1000, 2000 });
```

### C: `test-utils.h`

```c
#include "test-utils.h"

// Quick check
yoimiya_quick_test();

// Test simple proof
YoimiyaTestResult result = {0};
uint8_t witness[501];
for (int i = 0; i < 501; i++) witness[i] = 1;
yoimiya_test_simple_proof(500, witness, 501, srs, &result);

// Test batch aggregation
YoimiyaTestResult batch_result = {0};
yoimiya_test_batch_aggregation(10, 100, witness, 501, srs, &batch_result);

// Print results
yoimiya_print_result(&result);
```

## API Reference

### Core Classes/Functions

#### Python & Node.js - `YoimiyaTester`

**Constructor:**
- `YoimiyaTester(max_degree=2048)` - Initialize with SRS

**Methods:**
- `test_simple_proof(num_constraints, witness)` - Test single proof
- `test_batch_aggregation(num_proofs, constraints_per_proof, witness)` - Test batch
- `test_scalability(constraint_sizes)` - Test across standard sizes (100-2000)
- `test_large_constraints(constraint_sizes)` - Test large sizes (10K-1M)
- `test_batch_sizes(batch_sizes, constraints_per_proof)` - Test across batch sizes
- `run_full_test_suite()` - Run complete test suite

**Returns:**
- `TestResult` object with:
  - `status`: "PASSED" or "FAILED"
  - `prove_ms`: Proof generation time in milliseconds
  - `verify_ms`: Verification time in milliseconds
    - `proof_bytes`: Serialized proof size in bytes (simple proof tests)
    - `peak_rss_mb`: Peak resident memory observed during the test
  - `aggregate_ms`: Aggregation time (batch tests only)
  - `batch_verify_ms`: Batch verification time
    - `batch_bytes`: Serialized batch calldata size in bytes (batch tests only)
  - `error`: Error message if test failed

The Python, Node.js, and C# test helpers now all expose the same core telemetry fields for simple proofs and batch tests.

### C - Header Functions

**Initialization:**
- `yoimiya_test_simple_proof()` - Test single proof
- `yoimiya_test_batch_aggregation()` - Test batch
- `yoimiya_test_scalability()` - Test across sizes
- `yoimiya_test_batch_sizes()` - Test across batch sizes

**Utilities:**
- `yoimiya_time_ms()` - Get current time in milliseconds
- `yoimiya_print_result()` - Print single result
- `yoimiya_print_summary()` - Print multiple results
- `yoimiya_quick_test()` - Quick sanity check
- `yoimiya_default_witness()` - Get default witness data

## Example: Running Tests

### Python

```python
from libs.test_utils import YoimiyaTester

# Initialize tester
tester = YoimiyaTester(max_degree=2048)

# Run full test suite
print("Starting comprehensive tests...")
results = tester.run_full_test_suite()

# Results will show:
# - ✓ Simple proofs at 100, 500, 1000, 2000 constraints
# - ✓ Batch aggregation at 2, 5, 10 proofs
# - ✓ Large batch test (100 proofs)
# - ✓ Stress test (5000 constraints)
# - prove_ms, verify_ms, proof_bytes, and peak_rss_mb telemetry
```

**Output:**
```
Running Yoimiya Test Suite...
============================================================

[1/4] Testing simple proof generation and verification...
[2/4] Testing batch aggregation...
[3/4] Testing large batch (100 proofs)...
[4/4] Testing high-constraint proof...

============================================================
TEST SUMMARY
============================================================

Total tests: 14
✓ Passed: 14
✗ Failed: 0

Detailed Results:
------------------------------------------------------------
✓ simple_proof         | Constraints: 100    | Prove: 0.0812ms | Verify: 0.5923ms | Proof: 164 bytes | Peak RSS: 12.40 MB
✓ simple_proof         | Constraints: 500    | Prove: 0.2043ms | Verify: 0.6104ms | Proof: 164 bytes | Peak RSS: 12.58 MB
✓ simple_proof         | Constraints: 1000   | Prove: 0.3301ms | Verify: 0.5987ms | Proof: 164 bytes | Peak RSS: 12.91 MB
✓ simple_proof         | Constraints: 2000   | Prove: 0.6234ms | Verify: 0.6124ms | Proof: 164 bytes | Peak RSS: 13.34 MB
✓ batch_aggregation    | Proofs: 2          | Aggregate: 0.0026ms | Verify: 0.6210ms | Calldata: 275 bytes | Peak RSS: 13.51 MB
✓ batch_aggregation    | Proofs: 5          | Aggregate: 0.0095ms | Verify: 0.6345ms | Calldata: 275 bytes | Peak RSS: 13.76 MB
✓ batch_aggregation    | Proofs: 10         | Aggregate: 0.0187ms | Verify: 0.6521ms | Calldata: 275 bytes | Peak RSS: 14.02 MB
✓ batch_aggregation    | Proofs: 100        | Aggregate: 0.1923ms | Verify: 0.6789ms | Calldata: 275 bytes | Peak RSS: 16.25 MB
✓ simple_proof         | Constraints: 5000  | Prove: 1.5234ms | Verify: 0.6145ms | Proof: 164 bytes | Peak RSS: 14.88 MB

## Full Telemetry Benchmark

From the SDK root, run:

```bash
python benchmark_telemetry.py
```

This emits one CSV row per constraint size with:
- `constraints`
- `prove_ms`
- `verify_ms`
- `proof_bytes`
- `peak_rss_mb`
- `valid`
```

## What It Tests

### Proof Generation & Verification
- Generates zero-knowledge proofs of correct computation
- Verifies proofs using the SRS (Structured Reference String)
- Measures performance metrics for both operations

### Batch Aggregation
- Combines multiple proofs into a single aggregated proof
- Verifies the aggregated proof efficiently
- Demonstrates scalability benefits of proof aggregation

### Scalability
- Tests proof generation with increasing constraint counts
- Helps understand performance characteristics
- Validates overhead remains reasonable at scale

### Batch Sizes
- Tests aggregation with different numbers of proofs
- Shows how aggregation scales with batch size
- Evaluates cost/benefit of aggregation

## What It Does NOT Reveal

The test utilities are designed to help you validate the SDK without exposing:
- ❌ The cryptographic primitives (CDG, MIRA)
- ❌ The internal proof construction algorithm
- ❌ The verification circuit details
- ❌ Implementation-specific optimizations
- ❌ The source code build infrastructure

## Best Practices

1. **Run Before Integration** - Always run the full test suite before integrating SDK into your application
2. **Benchmark Your Use Case** - Use scalability tests to understandin performance for your constraints
3. **Verify on Target Platform** - Run tests on the actual platform you'll use
4. **Monitor Performance** - Use timing results to establish baselines for your application
5. **Test Different Batch Sizes** - Find optimal batch size for your aggregation use case

## Performance Baselines (Reference Hardware)

| Operation | Typical Time |
|-----------|--------------|
| Prove 100 constraints | 0.08 ms |
| Prove 500 constraints | 0.20 ms |
| Prove 1000 constraints | 0.33 ms |
| Prove 2000 constraints | 0.63 ms |
| Verify any proof | 0.59 ms |
| Aggregate 2 proofs | 0.0026 ms |
| Aggregate 5 proofs | 0.0095 ms |
| Aggregate 100 proofs | 0.19 ms |

**Note:** Times vary based on hardware. Run scalability tests on your target platform for accurate benchmarks.

## Integration Example

```python
# In your application
from libs.test_utils import YoimiyaTester

def validate_sdk():
    """Validate SDK works before running critical operations"""
    tester = YoimiyaTester()
    
    # Run quick check
    result = tester.test_simple_proof(num_constraints=100)
    if result['status'] != 'PASSED':
        raise RuntimeError("SDK validation failed!")
    
    return True

if __name__ == "__main__":
    validate_sdk()
    print("✓ SDK validated and ready to use")
```

## Testing Large Constraints (Dev Machine)

Developers can test proof generation with very large constraint counts (up to 1M) on their development machine to understand performance characteristics and find optimal parameters.

### Python Example

```python
from libs.test_utils import YoimiyaTester

# Create tester with larger SRS for big proofs
tester = YoimiyaTester(max_degree=1_000_000)

# Test across standard sizes first
print("Standard constraint tests:")
standard_results = tester.test_scalability([100, 500, 1000, 2000])

# Then test large sizes up to 1M
print("\nLarge constraint tests:")
large_results = tester.test_large_constraints([
    10_000,
    50_000,
    100_000,
    250_000,
    500_000,
    1_000_000
])

# Analyze results
for result in large_results:
    constraints = result.get('constraints')
    prove_time = result.get('prove_ms')
    verify_time = result.get('verify_ms')
    print(f"{constraints:,} constraints: Prove {prove_time}ms, Verify {verify_time}ms")
```

### Node.js Example

```javascript
const { YoimiyaTester } = require('./libs/test-utils.js');

async function testLargeConstraints() {
    // Create tester with larger SRS
    const tester = new YoimiyaTester(1_000_000);
    
    // Test large sizes
    const results = tester.testLargeConstraints([
        10_000,
        50_000,
        100_000,
        250_000,
        500_000,
        1_000_000
    ]);
    
    // Analyze performance
    for (const result of results) {
        console.log(`${result.constraints.toLocaleString()} constraints:`);
        console.log(`  Prove: ${result.prove_ms}ms`);
        console.log(`  Verify: ${result.verify_ms}ms`);
    }
}

testLargeConstraints();
```

### C# Example

```csharp
using Yoimiya.TestUtils;

class Program {
    static void Main() {
        // Create tester with larger SRS
        var tester = new YoimiyaTester(1_000_000);
        
        // Test large constraint sizes
        var results = tester.TestLargeConstraints(new[] {
            10_000,
            50_000,
            100_000,
            250_000,
            500_000,
            1_000_000
        });
        
        // Print results
        foreach (var result in results) {
            Console.WriteLine($"{result.Constraints:N0} constraints:");
            Console.WriteLine($"  Prove: {result.ProveMs}ms");
            Console.WriteLine($"  Verify: {result.VerifyMs}ms");
        }
    }
}
```

### Custom Constraint Testing

Test any constraint size you want:

```python
from libs.test_utils import YoimiyaTester

tester = YoimiyaTester(max_degree=2_000_000)

# Test your specific constraint requirements
my_constraints = [5_000, 25_000, 75_000, 150_000]
results = tester.test_large_constraints(my_constraints)
```

## Performance Expectations

### Standard Constraints (100-2000)
| Constraints | Prove Time | Verify Time |
|------------|-----------|------------|
| 100 | 0.08 ms | 0.59 ms |
| 500 | 0.20 ms | 0.59 ms |
| 1,000 | 0.33 ms | 0.59 ms |
| 2,000 | 0.63 ms | 0.59 ms |

### Large Constraints (10K-1M)
*Times are approximate and depend on hardware*

| Constraints | Approximate Time | Notes |
|------------|-----------------|-------|
| 10,000 | ~3-5 ms | Proof generation |
| 50,000 | ~15-25 ms | Linear scaling |
| 100,000 | ~30-50 ms | Optimal for most use cases |
| 250,000 | ~80-120 ms | Can still verify in ~1ms |
| 500,000 | ~160-240 ms | Very high throughput |
| 1,000,000 | ~330-500 ms | Maximum tested size |

**Important Notes:**
- Verification remains fast (~0.6-1ms) even at 1M constraints
- Proof generation time scales roughly linearly with constraint count
- Hardware and SRS generation affect absolute times
- Always test on your target deployment hardware

## Workflow: From Dev Testing to Production

### Phase 1: Dev Machine Testing
```
1. Start with standard constraints (100-2000)
2. Verify basic functionality works
3. Test your specific constraint count range
4. Measure performance on dev hardware
```

### Phase 2: Optimization
```
1. Identify your optimal constraint batch size
2. Test aggregation efficiency at your scale
3. Benchmark on representative hardware
4. Plan resource requirements
```

### Phase 3: Production Validation
```
1. Run full test suite with production SRS
2. Verify performance targets
3. Monitor real-world proof generation
4. Adjust parameters based on actual usage
```

## Integration Example

```python
# In your application
from libs.test_utils import YoimiyaTester

def validate_sdk():
    """Validate SDK works before running critical operations"""
    tester = YoimiyaTester()
    
    # Run quick check
    result = tester.test_simple_proof(num_constraints=100)
    if result['status'] != 'PASSED':
        raise RuntimeError("SDK validation failed!")
    
    return True

if __name__ == "__main__":
    validate_sdk()
    print("✓ SDK validated and ready to use")
```

## Troubleshooting

**Tests are failing?**
1. Verify binaries are correctly installed for your platform
2. Check that SRS generation succeeds
3. Ensure witness data format is correct
4. Review error messages in test results

**Performance is slower than expected?**
1. Run on release/optimized builds
2. Ensure GPU resources are available (if using GPU)
3. Check system load (other processes consuming CPU)
4. Run scalability tests to understand performance curve

**Unable to find binaries?**
1. Ensure you've extracted SDK binaries for your platform
2. Check `platforms/` directory has your platform binaries
3. Verify library paths are set correctly in your environment

## License

Business Source License 1.1 (BSL-1.1)

See LICENSE file for terms.
