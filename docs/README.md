# Yoimiya SDK Documentation

## Overview

Yoimiya is a universal zero-knowledge proof (ZK) system supporting multiple circuit formats (R1CS, ACIR, Plonkish) with KZG commitments and BN254 pairing verification. This SDK provides production-ready bindings for C, Python, Node.js, and C#.

## Features

- **Multi-format support**: R1CS, ACIR, Plonkish circuits
- **KZG commitments**: Efficient polynomial commitments
- **BN254 pairing**: Battle-tested cryptographic pairing
- **Batch aggregation**: Combine multiple proofs into a single batch proof
- **Super-batch aggregation**: Fold multiple batches into a single super-batch
- **Multi-batch verification**: Verify N batches in one EVM transaction
- **Hardware detection**: Auto-detect CPU and select optimal proving params
- **Precompiled SRS**: Bundled SRS tiers (no generation needed)
- **Multi-platform**: Windows, Linux, macOS, Android, iOS
- **Language bindings**: C, Python, Node.js, C#

## Installation

### C (Native)

1. Download the appropriate binary for your platform from releases
2. Link against `libyoimiya` or `libyoimiya.a`
3. Include `yoimiya.h` header

**Linux:**
```bash
gcc -o myapp myapp.c -L/path/to/sdk/lib -lyoimiya
```

**macOS:**
```bash
clang -o myapp myapp.c -L/path/to/sdk/lib -lyoimiya
```

**Windows:**
```cmd
cl myapp.c /link /LIBPATH:path\to\sdk\lib yoimiya.lib
```

### Python

```bash
pip install ./sdk/bindings/python
```

### Node.js

```bash
npm install ./sdk/bindings/nodejs
```

### C#

Add reference to `Yoimiya.cs` or compile as a shared library:
```bash
csc /target:library Yoimiya.cs
```

## Quick Start

### Python

```python
from yoimiya import generate_test_srs, prove_test, aggregate_proofs

# Generate SRS
srs = generate_test_srs(max_degree=1024)

# Prove
witness = [1, 2, 3, 4]
proof = prove_test(num_constraints=100, witness=witness, srs=srs)

# Verify
if proof.verify(srs):
    print("Proof is valid!")

# Aggregate
proofs = [proof1, proof2, proof3]
batch_proof = aggregate_proofs(proofs, srs)
if batch_proof.verify(srs):
    print("Batch proof is valid!")
```

### Node.js

```javascript
const { generateTestSrs, proveTest, aggregateProofs } = require('yoimiya-sdk');

// Generate SRS
const srs = generateTestSrs(1024);

// Prove
const witness = [1n, 2n, 3n, 4n];
const proof = proveTest(100, witness, srs);

// Verify
if (proof.verify(srs)) {
  console.log('Proof is valid!');
}

// Aggregate
const batchProof = aggregateProofs([proof1, proof2, proof3], srs);
if (batchProof.verify(srs)) {
  console.log('Batch proof is valid!');
}

// Cleanup
proof.destroy();
batchProof.destroy();
srs.destroy();
```

### C#

```csharp
using Yoimiya.SDK;

// Generate SRS
using var srs = YoimiyaSdk.GenerateTestSrs(1024);

// Prove
ulong[] witness = { 1, 2, 3, 4 };
using var proof = YoimiyaSdk.ProveTest(100, witness, srs);

// Verify
if (proof.Verify(srs)) {
    Console.WriteLine("Proof is valid!");
}

// Aggregate
var proofs = new List<Proof> { proof1, proof2, proof3 };
using var batchProof = YoimiyaSdk.AggregateProofs(proofs, srs);
if (batchProof.Verify(srs)) {
    Console.WriteLine("Batch proof is valid!");
}
```

### C (Native)

```c
#include <yoimiya.h>
#include <stdio.h>

int main() {
    // Generate SRS
    YoimiyaSrs* srs = yoimiya_generate_test_srs(1024);
    if (!srs) {
        fprintf(stderr, "Failed to generate SRS\n");
        return 1;
    }
    
    // Prove test circuit
    uint64_t witness[] = {1, 2, 3, 4};
    YoimiyaProof* proof = yoimiya_prove_test(
        100,  // num_constraints
        witness,
        4,    // witness_len
        srs
    );
    
    if (!proof) {
        fprintf(stderr, "Proving failed\n");
        yoimiya_free_srs(srs);
        return 1;
    }
    
    // Verify
    int result = yoimiya_verify(proof, srs);
    if (result == 1) {
        printf("Proof is valid!\n");
    }
    
    // Cleanup
    yoimiya_free_proof(proof);
    yoimiya_free_srs(srs);
    
    return 0;
}
```

## API Reference

### Structures

**Srs (Structured Reference String)**
- Contains polynomial commitments for proving and verification
- Generated once, reused for multiple proofs

**Proof**
- Single proof of a circuit execution
- Can be verified individually or aggregated

**BatchProof**
- Aggregated proof combining multiple individual proofs
- More efficient verification than individual proofs

### Functions

#### SRS Management

| Function | Description |
|----------|-------------|
| `generate_test_srs(max_degree)` | Generate a test SRS (deterministic) |
| `precompiled_test_srs(num_constraints)` | Get bundled SRS for constraint count (no generation) |
| `free_srs(srs)` | Free SRS resources |

#### Proving

| Function | Description |
|----------|-------------|
| `prove_test(num_constraints, witness, srs)` | Prove test circuit |
| `prove_test_precompiled(num_constraints, witness)` | Prove test circuit with bundled SRS |
| `prove_r1cs(r1cs_path, witness, srs)` | Prove R1CS circuit (Circom) with u64 witness |
| `prove_r1cs_field(r1cs_path, witness, srs)` | Prove R1CS circuit with 254-bit BN254 field-element witness (Circom native) |
| `prove_acir(acir_path, witness, srs)` | Prove ACIR circuit (Noir) |
| `prove_plonkish(plonkish_path, witness, srs)` | Prove Plonkish circuit (Halo2) |
| `free_proof(proof)` | Free proof resources |
| `proof_size_bytes(proof)` | Get compressed proof size |

#### Verification

| Function | Description |
|----------|-------------|
| `verify(proof, srs)` | Verify single proof (off-chain) |
| `verify_precompiled(proof)` | Verify with auto-selected bundled SRS |

#### Aggregation & TEE

| Function | Description |
|----------|-------------|
| `aggregate(proofs[], count, srs)` | Aggregate multiple proofs into batch |
| `aggregate_batches(batches[], count)` | Fold N batches into a super-batch |
| `multi_batch_calldata(batches[], count)` | Serialize N batches for `verifyMultiBatch()` |
| `batch_to_calldata(batch, buf, len)` | Serialize batch → 275-byte blob |
| `batch_proof_hash(batch, out)` | SHA-256 of blob — send to TEE for signing |
| `free_batch_proof(batch_proof)` | Free batch proof resources |

#### TEE Attestation (Optional)

Proving runs on the server. Only the 32-byte proof hash enters the TEE for signing.

```c
// 1. Prove and aggregate on server (full speed)
YoimiyaBatchProof* batch = yoimiya_aggregate(proofs, 3, srs);

// 2. Get hash — send to TEE, receive (r, s)
uint8_t blob[275], hash[32];
yoimiya_batch_to_calldata(batch, blob, 275);
yoimiya_batch_proof_hash(batch, hash);
// TEE signs hash → r[32], s[32]

// 3. Submit: verifyBatchWithAttestation(blob, r, s) — ~62k gas on L2
```

**One-time key pinning (owner, ~30k gas):**
```solidity
verifier.pinTeeKey(teeKeyX, teeKeyY);
```
Key is immutable after pinning. `verifyBatch()` continues to work without TEE.

#### Hardware Detection

| Function | Description |
|----------|-------------|
| `detect_hardware()` | Returns CPU info, tier, optimal partitions |
| `optimal_partitions(num_constraints)` | Get best partition count for constraint size |

## Platform Support

| Platform | Status | Architecture |
|----------|--------|--------------|
| Windows | ✅ | x86_64 |
| Linux | ✅ | x86_64 |
| macOS | ✅ | x86_64, ARM64 (Apple Silicon) |
| Android | ✅ | ARMv8 |
| iOS | ✅ | ARM64 |

## Building from Source

### Requirements
- Rust 1.70+
- Cargo
- Cross-compilation toolchains (for non-native targets)

### Build

```bash
# Build for current platform
cargo build --release

# Build for specific platform
./scripts/build-sdk.ps1 -Target linux-x86_64 -Release

# Build for all platforms
./scripts/build-sdk.ps1 -Release
```

### Binary locations
- Built libraries: `./target/<target>/release/`
- Bundled SDK: `./sdk/platforms/<platform>/`

## Performance

Benchmark results (Windows x86_64 reference hardware, March 2026):

**Proving (ms)**
- 100 constraints: 0.28 ms
- 500 constraints: 0.34 ms
- 1000 constraints: 0.49 ms
- 2000 constraints: 0.82 ms

**Verification**
- 1000 constraint proof: ~0.59 ms (constant regardless of constraint count)

**Aggregation**
- 2 proofs: 2.7 µs
- 5 proofs: 9.3 µs
- 10 proofs: 21.7 µs

**Rollup-scale super-batch (aggregate_batches)**
- 100 node batches → 1 on-chain submission: 0.42 ms
- 500 node batches → 1 on-chain submission: 4.92 ms
- 1,000 node batches → 1 on-chain submission: 16.9 ms

Note: super-batch produces the same 275-byte calldata as a single batch — on-chain gas does not change with batch size.

## On-Chain Verification

Two Solidity verifier contracts are provided:

| Contract | Gas (single) | Gas (multi-batch) | TEE-attested | Use case |
|----------|-------------|-------------------|--------------|----------|
| `YoimiyaBatchVerifier.sol` | ~58,000 | — | ~62,000 | Simple + TEE |
| `YoimiyaOptimizedVerifier.sol` | ~64,000 | ~22k/batch | — | High-throughput |

### Gas Cost Reference (L2: Base / OP Mainnet / Polygon zkEVM)

**YoimiyaBatchVerifier.sol**

| Function | Gas | ~USD (0.005 gwei, $2,500 ETH) | ~USD (L1, 10 gwei) |
|----------|-----|-------------------------------|--------------------|
| `pinTeeKey(x, y)` — one time | ~30,000 | < $0.001 | ~$0.75 |
| `verifyBatch(blob)` | ~58,000 | < $0.001 | ~$1.45 |
| `verifyBatchWithAttestation(blob, r, s)` | ~62,000 | < $0.001 | ~$8.25* |

\* L1 uses Solidity P-256 library until EIP-7212 is finalized (~272k extra gas).
On L2 with RIP-7212 (Base, OP Mainnet, Polygon zkEVM, zkSync, Scroll), P-256
costs only ~3,450 gas. **Deploy on L2 for sub-cent economics.**

**YoimiyaOptimizedVerifier.sol**

| Function | Gas | ~USD on L2 | Description |
|----------|-----|------------|-------------|
| `verifyBatch(bytes)` | ~64,000 | < $0.001 | Single batch, emit event |
| `verifyOnly(bytes)` | ~34,000 | < $0.001 | View-only, no state write |
| `verifyMultiBatch(bytes[])` | ~22k/batch | < $0.001/batch | N batches, 1 pairing check |
| `verifyMultiBatchView(bytes[])` | ~20k/batch | < $0.001/batch | View-only multi-batch |

### BN254 Precompile Breakdown

| Precompile | Address | Gas | Usage |
|------------|---------|-----|-------|
| `ecAdd` | 0x06 | ~150 | 2× per verify |
| `ecMul` | 0x07 | ~6,000 | 2× per verify |
| `ecPairing` | 0x08 | ~45,000 | 1× per verify |
| P-256 verify | 0x0100 | ~3,450 | 1× (TEE path, RIP-7212 chains) |

## Test Circuit Files

Sample circuit files for testing are available in releases:

| File | Format | Size | Constraints |
|------|--------|------|-------------|
| `test_circuit.r1cs` | R1CS (Circom) | 1,212 bytes | 10 |
| `test_circuit.acir` | ACIR (Noir) | 168 bytes | 10 |
| `test_circuit.plonkish` | Plonkish (Halo2) | 212 bytes | 10 |

## Examples

Complete examples are available in `examples/`:

- `C/`: Native C example
- `Python/`: Python integration example
- `Node.js/`: Node.js service example
- `C#/`: C# .NET example

## License

Business Source License 1.1 (BSL-1.1)

## Support

- **Issues**: https://github.com/atlasw231-maker/yoimiya-sdk/issues
- **Documentation**: https://docs.yoimiya.io
- **Email**: atlasw231@gmail.com

## Contributing

Contributions welcome! Please see CONTRIBUTING.md

## Related Links

- [Solidity Verifiers](../contracts/) — `YoimiyaBatchVerifier.sol` and `YoimiyaOptimizedVerifier.sol`
- [Repository](https://github.com/atlasw231-maker/yoimiya-sdk)
- [Atlas Protocol](https://atlasw231-maker.github.io)
- [RIP-7212 — P-256 precompile](https://github.com/ethereum/RIPs/blob/master/RIPS/rip-7212.md) — live on Base, OP Mainnet, Polygon zkEVM, zkSync, Scroll
