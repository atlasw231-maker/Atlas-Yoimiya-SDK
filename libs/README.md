# Test Utilities Library

High-level testing utilities for the Yoimiya SDK that make it easy to test proofs, batch operations, and performance characteristics without understanding the internal implementation.

## Overview

The test utilities provide:

- **Simple Proof Testing** - Generate and verify individual proofs with timing metrics
- **Batch Aggregation Testing** - Test proof aggregation and batch verification
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
uint8_t witness[] = {1, 2, 3, 4};
yoimiya_test_simple_proof(500, witness, 4, srs, &result);

// Test batch aggregation
YoimiyaTestResult batch_result = {0};
yoimiya_test_batch_aggregation(10, 100, witness, 4, srs, &batch_result);

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
- `test_scalability(constraint_sizes)` - Test across sizes
- `test_batch_sizes(batch_sizes, constraints_per_proof)` - Test across batch sizes
- `run_full_test_suite()` - Run complete test suite

**Returns:**
- `TestResult` object with:
  - `status`: "PASSED" or "FAILED"
  - `prove_ms`: Proof generation time in milliseconds
  - `verify_ms`: Verification time in milliseconds
  - `aggregate_ms`: Aggregation time (batch tests only)
  - `batch_verify_ms`: Batch verification time
  - `error`: Error message if test failed

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
✓ simple_proof         | Constraints: 100    | Prove: 0.0812ms | Verify: 0.5923ms
✓ simple_proof         | Constraints: 500    | Prove: 0.2043ms | Verify: 0.6104ms
✓ simple_proof         | Constraints: 1000   | Prove: 0.3301ms | Verify: 0.5987ms
✓ simple_proof         | Constraints: 2000   | Prove: 0.6234ms | Verify: 0.6124ms
✓ batch_aggregation    | Proofs: 2          | Aggregate: 0.0026ms | Verify: 0.6210ms
✓ batch_aggregation    | Proofs: 5          | Aggregate: 0.0095ms | Verify: 0.6345ms
✓ batch_aggregation    | Proofs: 10         | Aggregate: 0.0187ms | Verify: 0.6521ms
✓ batch_aggregation    | Proofs: 100        | Aggregate: 0.1923ms | Verify: 0.6789ms
✓ simple_proof         | Constraints: 5000  | Prove: 1.5234ms | Verify: 0.6145ms
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
