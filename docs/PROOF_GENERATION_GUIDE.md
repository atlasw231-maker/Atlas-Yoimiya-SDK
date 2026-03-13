# Developer Guide: Proof Generation & Testing

**How to generate proofs on your dev machine, test with constraints up to 1M, and optimize for production.**

---

## Quick Start

### 1. Initialize SRS (Structured Reference String)

```python
from yoimiya import generate_test_srs, prove_test

# Create SRS - reuse for multiple proofs
srs = generate_test_srs(max_degree=2048)
```

### 2. Generate a Proof

```python
# Define your computation (witness data)
num_constraints = 500
witness = [1] * (num_constraints + 1)

# Generate proof
proof = prove_test(
    num_constraints=num_constraints,
    witness=witness,
    srs=srs
)
```

**Important requirement:** For test circuits, witness length must be at least
`num_constraints + 1` (equivalently `witness_len > num_constraints`).

### 3. Verify the Proof

```python
# Verify locally (optional, useful for development)
is_valid = proof.verify(srs)
print(f"Proof valid: {is_valid}")
```

---

## Understanding Constraints

**Constraints** represent the complexity of your computation:

- **100 constraints** ~ Simple calculations (few operations)
- **1,000 constraints** ~ Standard computations (moderate operations)
- **100,000 constraints** ~ Complex operations (thousands of gates)
- **1,000,000 constraints** ~ Very large computations (millions of gates)

### Finding Your Constraint Count

1. **Estimate operations**: How many arithmetic operations does your computation require?
2. **Account for overhead**: ZK circuits typically need 2-5x more constraints than raw operations
3. **Test with ranges**: Generate test proofs with your estimated range
4. **Measure performance**: Find where prove time becomes acceptable for your use case

---

## Testing Framework

### Basic Testing (Standard Sizes)

```python
from libs.test_utils import YoimiyaTester

tester = YoimiyaTester(max_degree=2048)

# Test standard sizes: 100, 500, 1000, 2000
results = tester.test_scalability()
```

### Large Constraint Testing (10K - 1M)

```python
# For large proofs, create larger SRS
tester = YoimiyaTester(max_degree=1_000_000)

# Test 10K to 1M constraints
results = tester.test_large_constraints([
    10_000,
    50_000,
    100_000,
    250_000,
    500_000,
    1_000_000
])
```

### Custom Constraint Testing

```python
# Test your specific constraint requirements
my_sizes = [512, 2048, 5120]
results = tester.test_large_constraints(my_sizes)

# Analyze results
for result in results:
    print(f"Constraints: {result['constraints']}")
    print(f"  Prove: {result['prove_ms']}ms")
    print(f"  Verify: {result['verify_ms']}ms")
    print(f"  Valid: {result['proof_valid']}")
```

---

## Performance Baselines

### Reference Hardware Results

| Constraints | Prove Time | Verify Time | Notes |
|-------------|-----------|------------|-------|
| 100 | 0.08 ms | 0.59 ms | Minimal |
| 500 | 0.20 ms | 0.59 ms | Quick |
| 1,000 | 0.33 ms | 0.59 ms | Standard |
| 2,000 | 0.63 ms | 0.59 ms | Moderate |
| 10,000 | ~3-5 ms | ~1 ms | Significant |
| 50,000 | ~15-25 ms | ~1 ms | Complex |
| 100,000 | ~30-50 ms | ~1 ms | Very complex |
| 250,000 | ~80-120 ms | ~1 ms | High complexity |
| 500,000 | ~160-240 ms | ~1 ms | Extreme |
| 1,000,000 | ~330-500 ms | ~1 ms | Maximum |

**Important:** Times vary based on:
- CPU architecture and speed
- System load
- Available memory
- SRS pre-computation caching

Always test on your target deployment environment.

---

## Workflow: Dev to Production

### Phase 1: Development Testing

**Goal:** Understand your use case and find optimal parameters

```python
from libs.test_utils import YoimiyaTester

# Step 1: Sanity check
tester = YoimiyaTester()
quick_result = tester.test_simple_proof(100)
assert quick_result['status'] == 'PASSED', "SDK not working!"

# Step 2: Test standard sizes
standard = tester.test_scalability()

# Step 3: Identify your constraint range
# Based on your application requirements

# Step 4: Deep test your range
my_tester = YoimiyaTester(max_degree=250_000)
custom = my_tester.test_large_constraints([
    5_000, 10_000, 25_000, 50_000
])

# Step 5: Find sweet spot
# Pick constraint count that balances:
# - Performance (prove time acceptable)
# - Security (constraints adequate for your computation)
# - Cost (resource requirements)
```

### Phase 2: Performance Profiling

```python
import time
from yoimiya import generate_test_srs, prove_test

# Generate SRS for your constraint count
srs = generate_test_srs(max_degree=YOUR_CONSTRAINT_COUNT)

# Profile multiple runs
prove_times = []
verify_times = []

for i in range(10):  # Test 10 times for average
    start = time.perf_counter()
    proof = prove_test(YOUR_CONSTRAINT_COUNT, your_witness, srs)
    prove_times.append(time.perf_counter() - start)
    
    start = time.perf_counter()
    proof.verify(srs)
    verify_times.append(time.perf_counter() - start)

# Analyze
print(f"Prove time (avg): {sum(prove_times)/len(prove_times)*1000:.2f}ms")
print(f"Verify time (avg): {sum(verify_times)/len(verify_times)*1000:.2f}ms")
print(f"Prove time (max): {max(prove_times)*1000:.2f}ms")
print(f"Verify time (max): {max(verify_times)*1000:.2f}ms")
```

### Phase 3: Batch Optimization

```python
# If processing multiple proofs, test aggregation
tester = YoimiyaTester(max_degree=PROD_CONSTRAINT_COUNT)

# Find optimal batch size
for batch_size in [5, 10, 20, 50, 100]:
    result = tester.test_batch_aggregation(
        num_proofs=batch_size,
        constraints_per_proof=YOUR_CONSTRAINT_COUNT
    )
    print(f"Batch {batch_size}: " +
          f"Aggregate {result['aggregate_ms']}ms, " +
          f"Verify {result['batch_verify_ms']}ms")
```

### Phase 4: Production Deployment

```python
# In production code
from yoimiya import generate_test_srs, prove_test, aggregate_proofs

class ProofGenerator:
    def __init__(self, constraint_count, max_batch=50):
        self.constraint_count = constraint_count
        self.max_batch = max_batch
        # Initialize SRS once
        self.srs = generate_test_srs(max_degree=constraint_count * 2)
    
    def generate_proof(self, witness):
        """Generate single proof"""
        return prove_test(
            self.constraint_count,
            witness,
            self.srs
        )
    
    def batch_proofs(self, proofs):
        """Aggregate proofs for efficiency"""
        if len(proofs) > self.max_batch:
            raise ValueError(f"Batch too large (max {self.max_batch})")
        return aggregate_proofs(proofs, self.srs)
```

---

## Direct Proof Generation

For developers who want full control without test utilities:

```python
from yoimiya import generate_test_srs, prove_test

# Initialize once
srs = generate_test_srs(max_degree=1_000_000)

# Generate proof for any constraint count
proof = prove_test(
    num_constraints=500_000,
    witness=[1] * 500_001,
    srs=srs
)

# Use proof in your application
# - Verify locally for testing: proof.verify(srs)
# - Send to smart contract for on-chain verification
# - Store in database
# - Return to client
```

**See examples:**
- Python: `examples/proof_generation_guide.py`
- Node.js: `examples/proof_generation_guide.js`

---

## Common Issues & Solutions

### Issue: SRS generation takes too long

**Solution:** Generate SRS incrementally based on actual constraint needs

```python
# Instead of: (too large, slow)
srs = generate_test_srs(max_degree=10_000_000)

# Do this: (only generate what you need)
srs = generate_test_srs(max_degree=max(your_constraint_sizes) * 1.5)
```

### Issue: Proof generation is slower than expected

**Solution:** Profile your code and check these factors:

1. **SRS Reuse:** Are you reusing the same SRS for multiple proofs?
   ```python
   # Good - reuse SRS
   srs = generate_test_srs(2048)
   proof1 = prove_test(100, witness1, srs)
   proof2 = prove_test(100, witness2, srs)
   
   # Bad - regenerating SRS each time
   proof1 = prove_test(100, witness1, generate_test_srs(2048))
   proof2 = prove_test(100, witness2, generate_test_srs(2048))
   ```

2. **Hardware:** Run on target deployment hardware
   - Local dev machine may be much slower
   - Cloud VM performance varies
   - GPU acceleration differences

3. **System Load:** Run on idle system
   - Other processes consuming CPU
   - Memory pressure
   - I/O contention

### Issue: Cannot test constraints > some value

**Solution:** Generate larger SRS

```python
# If you need 500K constraints but SRS maxes at 256K:
try:
    srs = generate_test_srs(max_degree=500_000)
    proof = prove_test(500_000, witness, srs)
except Exception as e:
    print(f"Constraint count too large: {e}")
    # Either reduce constraints or upgrade hardware
```

### Issue: Memory usage is very high

**Solution:** Process proofs in batches

```python
# Instead of: (loads all in memory)
all_proofs = [prove_test(1000, wx, srs) for wx in witness_list]
batch = aggregate_proofs(all_proofs, srs)

# Do this: (process in chunks)
batch_size = 50
all_batches = []

for i in range(0, len(witness_list), batch_size):
    chunk_proofs = [
        prove_test(1000, wx, srs)
        for wx in witness_list[i:i + batch_size]
    ]
    batch = aggregate_proofs(chunk_proofs, srs)
    all_batches.append(batch)
```

---

## Best Practices

### ✓ DO:

- **Reuse SRS** for multiple proofs
- **Pre-compute SRS** before time-critical sections
- **Test on target hardware** with actual constraint counts
- **Profile your code** to identify bottlenecks
- **Batch proofs** when you have multiple to aggregate
- **Cache verification results** if calling frequently

### ✗ DON'T:

- **Regenerate SRS** repeatedly
- **Test with toy constraints** then expect prod to work at scale
- **Assume local perf = cloud perf**
- **Process unlimited batches** without memory limits
- **Verify proofs repeatedly** without caching
- **Mix very different constraint counts** without regenerating SRS

---

## Testing Checklist

Before deploying to production:

- [ ] SDK works with `quick_test()`
- [ ] Standard constraints (100-2000) work correctly
- [ ] Your specific constraint counts work correctly
- [ ] Performance is acceptable (< your timeout threshold)
- [ ] Memory usage is within limits
- [ ] Error handling works (invalid proofs detected)
- [ ] Batch aggregation works at scale
- [ ] SRS regeneration is handled correctly
- [ ] Witness data format is correct
- [ ] Verification works with generated proofs

---

## Performance Tips

### Tip 1: Pre-warm SRS

```python
# Generate SRS in advance
srs = generate_test_srs(max_degree=critical_constraint_count)
# Now time-critical code uses pre-generated SRS
```

### Tip 2: Use batch aggregation

```python
# Verification is much faster for batches
single_proofs = [proof1, proof2, proof3]  # 3 verifications
batch_proof = aggregate_proofs(single_proofs, srs)
batch_proof.verify(srs)  # 1 verification
```

### Tip 3: Profile constraint sizing

```python
# Find minimum constraints adequate for your computation
for constraints in [100, 500, 1000, 5000, 10000]:
    proof = prove_test(constraints, my_witness, srs)
    if proof.verify(srs):
        print(f"OK: {constraints} constraints sufficient")
        break
```

---

## Next Steps

1. **Run the test suite:** `python libs/test-utils.py`
2. **Test your constraint range:** See code examples above
3. **Profile performance:** Use `examples/proof_generation_guide.py`
4. **Integrate into your app:** See integration examples
5. **Monitor in production:** Track proof times and resource usage

For more information, see:
- `libs/README.md` - Test utilities API
- `examples/proof_generation_guide.py` - Python examples
- `examples/proof_generation_guide.js` - Node.js examples
- Full SDK docs in `docs/README.md`
