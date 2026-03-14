# Developer Guide: Proof Generation & Testing

**How to generate proofs on your dev machine, test with constraints up to 1M, and optimize for production.**

Supports all circuit formats: **R1CS**, **ACIR** (Noir), **Plonkish** (Halo2)

---

## Quick Start

### 1. Initialize SRS (Structured Reference String)

**Option A: Generate SRS (for custom sizes)**
```python
from yoimiya import generate_test_srs, prove_test

# Create SRS for up to 2048 constraints
srs = generate_test_srs(max_degree=2048)
```

**Option B: Use Precompiled SRS (no generation needed)**
```python
from yoimiya import precompiled_test_srs

# Bundled SRS - auto-selects tier for your constraint count
srs = precompiled_test_srs(num_constraints=1000)
```

### 2. Generate a Proof

**Test Circuit (synthetic):**
```python
proof = prove_test(
    num_constraints=500,
    witness=[1] * 501,  # witness_len must be > num_constraints
    srs=srs
)
```

**R1CS Circuit (Circom):**
```python
from yoimiya import prove_r1cs

proof = prove_r1cs(
    path="path/to/circuit.r1cs",
    witness=[1, 2, 3, ...],
    srs=srs
)
```

**ACIR Circuit (Noir):**
```python
from yoimiya import prove_acir

proof = prove_acir(
    path="path/to/circuit.acir",
    witness=[1, 2, 3, ...],
    srs=srs
)
```

**Plonkish Circuit (Halo2):**
```python
from yoimiya import prove_plonkish

proof = prove_plonkish(
    path="path/to/circuit.plonkish",
    witness=[1, 2, 3, ...],
    srs=srs
)
```

### 3. Verify the Proof

**Local Verification (off-chain):**
```python
is_valid = proof.verify(srs)
print(f"Proof valid: {is_valid}")
```

**With Precompiled SRS (no SRS parameter needed):**
```python
from yoimiya import verify_precompiled

is_valid = verify_precompiled(proof)
print(f"Proof valid: {is_valid}")
```

### 4. Aggregate Multiple Proofs

**Level 1: Basic Aggregation**
```python
from yoimiya import aggregate_proofs

proofs = [proof1, proof2, proof3]
batch_proof = aggregate_proofs(proofs, srs)
assert batch_proof.verify(srs)
```

**Level 2: Super-Batch (fold multiple batches)**
```python
from yoimiya import aggregate_batches

batch_a = aggregate_proofs(proofs_a, srs)
batch_b = aggregate_proofs(proofs_b, srs)

super_batch = aggregate_batches([batch_a, batch_b])
assert super_batch.verify(srs)
```

### 5. Prepare for On-Chain Submission

**Single batch:**
```python
calldata = batch_proof.to_calldata()  # 275 bytes fixed
# Submit to YoimiyaBatchVerifier.sol or YoimiyaOptimizedVerifier.sol
```

**Multiple batches (multi-batch on-chain):**
```python
from yoimiya import multi_batch_calldata

blobs = multi_batch_calldata([batch1, batch2, batch3])
# Each blob is 275 bytes, submit to verifyMultiBatch()
# Gas savings: ~22k/batch instead of ~64k/batch
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

## Testing with Sample Circuits

Test circuits are included in the release:

```python
from yoimiya import prove_r1cs, prove_acir, prove_plonkish, verify

srs = generate_test_srs(max_degree=4096)

# All use 10 constraints, witness = [1, 1, ..., 1]
proof_r1cs = prove_r1cs("examples/circuits/test_circuit.r1cs", [1]*12, srs)
proof_acir = prove_acir("examples/circuits/test_circuit.acir", [1]*13, srs)
proof_plonkish = prove_plonkish("examples/circuits/test_circuit.plonkish", [1]*32, srs)

assert verify(proof_r1cs, srs)
assert verify(proof_acir, srs)
assert verify(proof_plonkish, srs)
print("✓ All sample circuits verified!")
```

## Custom Scalability Testing

```python
from yoimiya import generate_test_srs, prove_test, verify
import time

# Test various constraint sizes
for n_constraints in [100, 500, 1000, 5000, 10000]:
    srs = generate_test_srs(max_degree=n_constraints+1)
    witness = [1] * (n_constraints + 1)
    
    start = time.perf_counter()
    proof = prove_test(n_constraints, witness, srs)
    prove_time = (time.perf_counter() - start) * 1000
    
    start = time.perf_counter()
    valid = verify(proof, srs)
    verify_time = (time.perf_counter() - start) * 1000
    
    print(f"Constraints: {n_constraints:6d} | Prove: {prove_time:6.2f}ms | Verify: {verify_time:6.2f}ms | Valid: {valid}")
```

---

## Performance Baselines

### Reference Hardware Results (March 2026)

| Constraints | Prove Time | Verify Time | Peak RAM | Valid |
|-------------|-----------|------------|----------|-------|
| 100 | 0.24 ms | 0.77 ms | 24.2 MB | ✓ |
| 500 | 0.53 ms | 0.74 ms | 24.7 MB | ✓ |
| 1,000 | 0.99 ms | 0.72 ms | 25.1 MB | ✓ |
| 2,000 | 1.76 ms | 0.83 ms | 25.1 MB | ✓ |
| 10,000 | 8.66 ms | 0.71 ms | 31.6 MB | ✓ |
| 50,000 | 52.98 ms | 0.72 ms | 55.6 MB | ✓ |
| 100,000 | 122.37 ms | 0.73 ms | 155.0 MB | ✓ |
| 250,000 | 340.74 ms | 0.78 ms | 235.6 MB | ✓ |
| 500,000 | 717.92 ms | 0.82 ms | 368.3 MB | ✓ |
| 1,000,000 | 1485.96 ms | 0.85 ms | 637.7 MB | ✓ |

**Notes:**
- Times measured using precompiled SRS (3 iterations, averaging steady-state performance)
- First iteration may be slower due to cache warming
- Verify time is ~0.7ms regardless of constraint count (thanks to KZG batch checking)
- Memory based on peak usage during proving
- Tested on reference hardware (March 14, 2026)

**Important:** Times vary significantly based on:
- CPU architecture and speed
- System load and background processes
- Available memory bandwidth
- SRS caching and pre-computation

Always benchmark on your target deployment environment.

**Rule of thumb:** Proving time scales roughly **O(n log n)** with constraint count.

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

### Phase 3: Aggregation & On-Chain Optimization

```python
from yoimiya import aggregate_proofs, multi_batch_calldata

# Prove 10 circuits
proofs = []
for i in range(10):
    proof = prove_test(1000, [1]*1001, srs)
    proofs.append(proof)

# Aggregate into single batch (~64k gas)
batch = aggregate_proofs(proofs, srs)
calldata = batch.to_calldata()  # 275 bytes

# Multiple batches (multi-batch ~22k/batch gas)
blobs = multi_batch_calldata([batch1, batch2, batch3])
for blob in blobs:
    submit_to_verifyMultiBatch(blob)  # More efficient!
```

### Phase 4: Hardware Detection

Optimize proving for your deployment environment:

```python
from yoimiya import detect_hardware, prove_test

hw = detect_hardware()
print(f"CPU cores: {hw.cores}")
print(f"Tier: {hw.tier}")  # Low, Mid, High, Server
print(f"Optimal partitions: {hw.optimal_partitions}")

# Proving automatically uses detected optimal settings
proof = prove_test(num_constraints, witness, srs)
```

**Tier Selection:**

| Tier | Cores | Default partitions | Example devices |
|------|-------|--------------------|----------|
| Low | 1–2 | 1 | Embedded, low-end phones |
| Mid | 3–4 | 2 | Budget phones, Chromebooks |
| High | 5–8 | 4 | Flagship phones, laptops |
| Server | 9+ | 8 | Cloud, workstations |

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
