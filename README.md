# Yoimiya Binary SDK

**Production-ready Zero-Knowledge Proving SDK with multi-platform binaries and language bindings.**

## 🎯 What It Does

Yoimiya SDK enables you to:

- **Generate cryptographic proofs** that verify computational claims without revealing the underlying data
- **Verify proofs efficiently** with minimal computational overhead
- **Aggregate multiple proofs** into single proofs for scalable verification
- **Integrate ZK proving** into applications across platforms: Web, Mobile, Cloud, and Edge

## 🔧 Problems It Solves

| Problem | Solution |
|---------|----------|
| **Scalability** | Aggregate thousands of proofs into one, reducing on-chain verification cost |
| **Privacy** | Prove correctness of computations without exposing sensitive data |
| **Cross-Platform** | Use the same proving engine across Windows, Linux, macOS, Android, iOS |
| **Language Flexibility** | Integrate via Python, Node.js, C#, or C—pick your stack |
| **Performance** | Sub-millisecond proof generation and verification |
| **Accessibility** | Pre-compiled binaries—no build infrastructure needed |

## 🌍 Platform & Language Support

| Platform | Status | Architecture |
|----------|--------|--------------|
| **Windows** | ✅ | x86_64 |
| **Linux** | ✅ | x86_64 |
| **macOS** | ✅ | x86_64, ARM64 (Apple Silicon) |
| **Android** | ✅ | ARMv8 |
| **iOS** | ✅ | ARM64 |

**Language Bindings:** C • Python • Node.js • C#

---

## 📦 Quick Start

### Extract the SDK

```bash
# Unix-like systems
tar -xzf yoimiya-sdk-v0.1.0.tar.gz

# Windows
unzip yoimiya-sdk-v0.1.0.zip
```

### Structure

```
sdk/
├── platforms/          # Pre-built binaries for each platform
│   ├── windows-x86_64/
│   ├── linux-x86_64/
│   ├── macos-x86_64/
│   ├── macos-aarch64/
│   ├── android-armv8/
│   └── ios-arm64/
├── include/            # C headers
├── bindings/           # Language-specific bindings
│   ├── python/         # Python ctypes bindings
│   ├── nodejs/         # Node.js FFI bindings
│   └── csharp/         # C# P/Invoke bindings
├── examples/           # Complete working examples
└── docs/               # Full documentation
```

---

## 🚀 Installation

### Python

```bash
cd sdk/bindings/python
pip install .
```

**Usage:**
```python
from yoimiya import generate_test_srs, prove_test, aggregate_proofs

srs = generate_test_srs(max_degree=2048)
proof = prove_test(num_constraints=500, witness=[1,2,3,4], srs=srs)
assert proof.verify(srs)
```

### Node.js

```bash
cd sdk/bindings/nodejs
npm install
```

**Usage:**
```javascript
const { generateTestSrs, proveTest } = require('yoimiya-sdk');

const srs = generateTestSrs(2048);
const proof = proveTest(500, [1n, 2n, 3n, 4n], srs);
console.log(proof.verify(srs)); // true
```

### C

**Link with native library:**

```bash
gcc -o myapp myapp.c \
  -I./sdk/include \
  -L./sdk/platforms/linux-x86_64 \
  -lyoimiya
```

**Usage:**
```c
#include <yoimiya.h>

YoimiyaSrs* srs = yoimiya_generate_test_srs(2048);
YoimiyaProof* proof = yoimiya_prove_test(500, witness, len, srs);
int valid = yoimiya_verify(proof, srs);  // 1 = valid, 0 = invalid
yoimiya_free_proof(proof);
yoimiya_free_srs(srs);
```

### C#

**Add reference and use:**

```csharp
using Yoimiya.SDK;

var srs = YoimiyaSdk.GenerateTestSrs(2048);
var proof = YoimiyaSdk.ProveTest(500, witness, srs);
bool valid = proof.Verify(srs);
```

---

## 📊 Performance

**Benchmark Results** (Reference hardware):

| Operation | Time |
|-----------|------|
| Prove 100 constraints | 0.08 ms |
| Prove 500 constraints | 0.20 ms |
| Prove 1000 constraints | 0.33 ms |
| Prove 2000 constraints | 0.63 ms |
| Verify proof (1000 constraints) | 0.59 ms |
| Aggregate 2 proofs | 0.0026 ms |
| Aggregate 5 proofs | 0.0095 ms |

---

## 📚 Examples

Each language has a complete working example:

- **C**: `sdk/examples/c_example.c` — Full workflow example
- **Python**: `sdk/examples/python_example.py` — Integration example
- **Node.js**: `sdk/examples/nodejs_example.js` — Service example
- **C#**: Check `sdk/docs/` for usage patterns

### Run Examples

```bash
# Python
cd sdk/examples
python3 python_example.py

# Node.js
cd sdk/bindings/nodejs
node ../../../examples/nodejs_example.js

# C
cd sdk/examples
gcc -o c_example c_example.c \
  -I../include \
  -L../platforms/linux-x86_64 \
  -lyoimiya
./c_example
```

---

##  API Overview

### Core Types

| Type | Purpose |
|------|---------|
| `Srs` | Structured Reference String for proving/verification |
| `Proof` | Single circuit proof |
| `BatchProof` | Aggregated batch of proofs |

### Core Functions

| Function | Purpose |
|----------|---------|
| `generate_test_srs(max_degree)` | Generate SRS |
| `prove_test(constraints, witness, srs)` | Prove test circuit |
| `verify(proof, srs)` | Verify single proof |
| `aggregate_proofs(proofs[], srs)` | Aggregate proofs |
| `verify_batch(batch_proof, srs)` | Verify batch proof |

---

## 💡 Common Tasks

### Generate Proofs on Your Dev Machine

```python
# Python
from yoimiya import generate_test_srs, prove_test

srs = generate_test_srs(max_degree=2048)
proof = prove_test(
    num_constraints=1000,
    witness=[1,2,3,4],
    srs=srs
)
assert proof.verify(srs), "Proof failed!"
```

**Test with large constraints:**
```python
# Test up to 1M constraints
from libs.test_utils import YoimiyaTester

tester = YoimiyaTester(max_degree=1_000_000)
results = tester.test_large_constraints([
    50_000, 100_000, 250_000, 500_000, 1_000_000
])
```

**See** [PROOF_GENERATION_GUIDE.md](docs/PROOF_GENERATION_GUIDE.md) for complete developer guide.

### Prove and Verify

```python
# Generate one-time SRS
srs = generate_test_srs(max_degree=2048)

# Prove a circuit
proof = prove_test(
    num_constraints=100,
    witness=[1, 2, 3, 4],
    srs=srs
)

# Verify locally (off-chain)
assert proof.verify(srs), "Proof invalid!"
```

### Batch Processing

```python
# Collect multiple proofs
proofs = []
for witness_data in batch_witnesses:
    proof = prove_test(100, witness_data, srs)
    proofs.append(proof)

# Aggregate into single proof
batch_proof = aggregate_proofs(proofs, srs)

# Verify batch (more efficient)
assert batch_proof.verify(srs), "Batch proof invalid!"
```

---

## 📖 Full Documentation

See `sdk/docs/README.md` for:
- Detailed API reference
- Complete examples for each language
- Performance metrics
- Contract integration guide
- Troubleshooting

---

## � Links

- **Repository**: https://github.com/atlasw231-maker/Atlas-Yoimiya-SDK
- **Issues**: https://github.com/atlasw231-maker/Atlas-Yoimiya-SDK/issues
- **Solidity Verifier**: See `contracts/YoimiyaBatchVerifier.sol`

---

## 🤝 Support

- **Documentation**: `sdk/docs/`
- **Examples**: `sdk/examples/`
- **Issues**: https://github.com/atlasw231-maker/Atlas-Yoimiya-SDK/issues
- **Email**: atlasw231@gmail.com

---

**Built with ❤️ by Atlas Protocol**
