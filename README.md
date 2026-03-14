# Yoimiya Binary SDK

**Production-ready, pre-built Zero-Knowledge Proving SDK for Windows, Linux, macOS, Android, and iOS.**

This is the **binary distribution**—no compilation needed. Choose your platform and language binding below.

| Platform | Status | Architecture |
|----------|--------|--------------|
| **Windows** | ✅ | x86_64 |
| **Linux** | ✅ | x86_64 |
| **macOS** | ✅ | x86_64, ARM64 (Apple Silicon) |
| **Android** | ✅ | ARMv8 |
| **iOS** | ✅ | ARM64 |

**Language Bindings:** C • Python • Node.js • C#

---

## 📦 Getting Started

**Step 1: Download** — Get the binary SDK from [releases](https://github.com/atlasw231-maker/Atlas-Yoimiya-SDK/releases)

**Step 2: Extract**
```bash
# Unix-like systems
tar -xzf yoimiya-sdk-v0.1.0.tar.gz
cd yoimiya-sdk-0.1.0

# Windows
unzip yoimiya-sdk-v0.1.0.zip
cd yoimiya-sdk-0.1.0
```

**Step 3: Choose your language** — Pick Python, Node.js, C, or C# below.

All libraries are pre-built. No compilation required.

---

## � What's Included

```
yoimiya-sdk-0.1.0/
├── platforms/              ← Pre-built binaries (pick your OS)
│   ├── windows-x86_64/     ← Windows users
│   ├── linux-x86_64/       ← Linux x86_64 users
│   ├── macos-x86_64/       ← macOS Intel users
│   ├── macos-aarch64/      ← macOS Apple Silicon users  
│   ├── android-armv8/      ← Android users
│   └── ios-arm64/          ← iOS users
│
├── include/                ← C header file (yoimiya.h)
│
├── bindings/               ← Language-specific bindings
│   ├── python/             ← Python: pip install .
│   ├── nodejs/             ← Node.js: npm install
│   └── csharp/             ← C#: binding code
│
├── examples/               ← Working example programs
│   ├── c_example.c
│   ├── python_example.py
│   ├── nodejs_example.js
│   └── circuits/           ← Test circuit files
│       ├── test_circuit.r1cs
│       ├── test_circuit.acir
│       └── test_circuit.plonkish
│
└── docs/                   ← Full API documentation
```

---

## �🚀 Installation by Language

### Python

```bash
cd bindings/python
pip install .
```

**First proof:**
```python
from yoimiya import generate_test_srs, prove_test

srs = generate_test_srs(max_degree=2048)
proof = prove_test(num_constraints=500, witness=[1,2,3,4], srs=srs)
assert proof.verify(srs)
print("✓ Proof valid!")
```

**With circuit files:**
```python
from yoimiya import prove_r1cs, prove_acir, prove_plonkish

proof_r1cs = prove_r1cs("path/to/circuit.r1cs", witness=[1,2,3], srs=srs)
proof_acir = prove_acir("path/to/circuit.acir", witness=[1,2,3], srs=srs)
proof_plonkish = prove_plonkish("path/to/circuit.plonkish", witness=[1,2,3], srs=srs)
```

Test circuit files are in `examples/circuits/` for quick testing.

### Node.js

```bash
cd bindings/nodejs
npm install
node  # Interactive REPL
```

**First proof:**
```javascript
const { generateTestSrs, proveTest } = require('yoimiya-sdk');

const srs = generateTestSrs(2048);
const proof = proveTest(500, [1n, 2n, 3n, 4n], srs);
console.log(proof.verify(srs)); // true
```

### C

**Link with pre-built library:**

**On Linux:**
```bash
gcc -o myapp myapp.c \
  -I./include \
  -L./platforms/linux-x86_64 \
  -lyoimiya
./myapp
```

**On Windows (MSVC):**
```cmd
cl myapp.c /I.\include /link /LIBPATH:.\platforms\windows-x86_64 yoimiya.lib
myapp.exe
```

**On macOS:**
```bash
clang -o myapp myapp.c \
  -I./include \
  -L./platforms/macos-x86_64 \
  -lyoimiya
./myapp
```

**Sample code:**
```c
#include <yoimiya.h>

YoimiyaSrs* srs = yoimiya_generate_test_srs(2048);
YoimiyaProof* proof = yoimiya_prove_test(500, witness, len, srs);
int valid = yoimiya_verify(proof, srs);  // 1 = valid, 0 = invalid
yoimiya_free_proof(proof);
yoimiya_free_srs(srs);
```

### C#

**Add the binding and use:**

```csharp
using Yoimiya.SDK;

var srs = YoimiyaSdk.GenerateTestSrs(2048);
var proof = YoimiyaSdk.ProveTest(500, witness, srs);
bool valid = proof.Verify(srs);
Console.WriteLine(valid ? "✓ Proof valid!" : "✗ Proof invalid!");
```

Full binding: `bindings/csharp/Yoimiya.cs`

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

- **C**: `examples/c_example.c` — Full workflow example
- **Python**: `examples/python_example.py` — Integration example
- **Node.js**: `examples/nodejs_example.js` — Service example
- **C#**: Check `docs/` for usage patterns

### Run Examples

```bash
# Python
cd examples
python3 python_example.py

# Node.js  
node nodejs_example.js

# C
gcc -o c_example c_example.c \
  -I../include \
  -L../platforms/linux-x86_64 \
  -lyoimiya
./c_example
```

---

## 🔧 Building from Source (SDK Developers Only)

This is a **binary distribution**—you don't need to build anything.

To modify the SDK source or rebuild binaries for a new platform:

1. Clone the [source repo](https://github.com/atlasw231-maker/Yoimiya-SDK)
2. See the **[private repo README](https://github.com/atlasw231-maker/Yoimiya-SDK/blob/main/README.md)** for build instructions

**Note:** Source builds require Rust 1.70+ and platform-specific toolchains.

---

## 🔗 API Overview

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
| `precompiled_test_srs(num_constraints)` | Get bundled SRS (no generation) |
| `prove_test(constraints, witness, srs)` | Prove test circuit |
| `prove_test_precompiled(constraints, witness)` | Prove with bundled SRS |
| `prove_r1cs(path, witness, srs)` | Prove R1CS circuit file |
| `prove_acir(path, witness, srs)` | Prove ACIR circuit file (Noir) |
| `prove_plonkish(path, witness, srs)` | Prove Plonkish circuit file (Halo2) |
| `verify(proof, srs)` | Verify single proof |
| `verify_precompiled(proof)` | Verify with bundled SRS |
| `aggregate_proofs(proofs[], srs)` | Aggregate proofs into batch |
| `aggregate_batches(batches[])` | Fold batches into super-batch |
| `multi_batch_calldata(batches[])` | Serialize N batches for multi-batch verify |
| `detect_hardware()` | Get CPU info and optimal parameters |

---

## 💡 Common Tasks

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

# Aggregate into single batch proof
batch_proof = aggregate_proofs(proofs, srs)

# Verify batch (more efficient)
assert batch_proof.verify(srs), "Batch proof invalid!"
```

### Super-Batch Aggregation (Batch-of-Batches)

```python
# Level 1: Each service creates its own batch
batch_a = aggregate_proofs(proofs_a, srs)
batch_b = aggregate_proofs(proofs_b, srs)

# Level 2: Fold all batches into one super-batch
super_batch = aggregate_batches([batch_a, batch_b])

# Serialize for on-chain multi-batch verification
blobs = multi_batch_calldata([batch_a, batch_b])
```

### On-Chain Verification

Two Solidity contracts are provided:

| Contract | Gas (single) | Multi-batch |
|----------|-------------|-------------|
| `YoimiyaBatchVerifier.sol` | ~95,000 | — |
| `YoimiyaOptimizedVerifier.sol` | ~64,000 | ~22k/batch |

---

## 📖 Full Documentation

See `docs/README.md` for:
- Detailed API reference
- Complete examples for each language
- Performance metrics
- On-chain verification guide
- Troubleshooting

---

## 📄 License

**Business Source License 1.1 (BSL-1.1)**

See LICENSE file for terms.

---

## 🔗 Links

- **Repository**: https://github.com/atlasw231-maker/yoimiya-sdk
- **Issues**: https://github.com/atlasw231-maker/yoimiya-sdk/issues
- **Solidity Verifiers**: See `contracts/YoimiyaBatchVerifier.sol` and `contracts/YoimiyaOptimizedVerifier.sol`
- **Test Circuit Files**: `test_circuit.r1cs`, `test_circuit.acir`, `test_circuit.plonkish` available in releases

---

## 🤝 Support

- **Documentation**: `sdk/docs/`
- **Examples**: `sdk/examples/`
- **Issues**: https://github.com/atlasw231-maker/yoimiya-sdk/issues
- **Email**: atlasw231@gmail.com

---

**Built with ❤️ by Atlas Protocol**
