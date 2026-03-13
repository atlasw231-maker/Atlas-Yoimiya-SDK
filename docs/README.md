# Yoimiya SDK Documentation

## Overview

Yoimiya is a universal zero-knowledge proof (ZK) system supporting multiple circuit formats (R1CS, ACIR, Plonkish) with KZG commitments and BN254 pairing verification. This SDK provides production-ready bindings for C, Python, Node.js, and C#.

## Features

- **Multi-format support**: R1CS, ACIR, Plonkish circuits
- **KZG commitments**: Efficient polynomial commitments
- **BN254 pairing**: Battle-tested cryptographic pairing
- **Batch aggregation**: Combine multiple proofs into a single batch proof
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
| `free_srs(srs)` | Free SRS resources |

#### Proving

| Function | Description |
|----------|-------------|
| `prove_test(num_constraints, witness, srs)` | Prove test circuit |
| `prove_r1cs(r1cs_path, witness, srs)` | Prove R1CS circuit |
| `free_proof(proof)` | Free proof resources |

#### Verification

| Function | Description |
|----------|-------------|
| `verify(proof, srs)` | Verify single proof (local, off-chain) |
| `verify_batch(batch_proof, srs)` | Verify batch proof |

#### Aggregation

| Function | Description |
|----------|-------------|
| `aggregate(proofs[], count, srs)` | Aggregate multiple proofs |
| `free_batch_proof(batch_proof)` | Free batch proof resources |

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

Benchmark results (running on reference hardware):

**Proving (ms)**
- 100 constraints: 0.08 ms
- 500 constraints: 0.20 ms
- 1000 constraints: 0.33 ms
- 2000 constraints: 0.63 ms

**Verification**
- 1000 constraint proof: 0.59 ms

**Aggregation**
- 2 proofs: 0.0026 ms
- 5 proofs: 0.0095 ms

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

- [Solidity Verifier](../contracts/YoimiyaBatchVerifier.sol)
- [Repository](https://github.com/atlasw231-maker/yoimiya-sdk)
- [Atlas Protocol](https://atlasw231-maker.github.io)
