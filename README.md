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

### ✅ Release Assets Are Available

Download from: https://github.com/atlasw231-maker/Atlas-Yoimiya-SDK/releases/tag/v0.1.0

Required binary per platform:

| Platform | Binary Asset |
|----------|--------------|
| Windows x86_64 | `yoimiya-windows-x86_64.dll` |
| Linux x86_64 | `libyoimiya-linux-x86_64.so` |
| macOS x86_64 | `libyoimiya-macos-x86_64.dylib` |
| macOS ARM64 | `libyoimiya-macos-aarch64.dylib` |
| Android ARMv8 | `libyoimiya-android-armv8.so` |
| iOS ARM64 | `libyoimiya-ios-arm64.a` |

Place the binary in `platforms/<your-platform>/` (or `bindings/python/` for quick Python testing).

### ✅ Must-Pass Validation Checklist (All Devs)

Before writing app code, run this checklist exactly once:

1. Download the binary that matches your OS + architecture from the release page.
2. Ensure the filename includes your platform explicitly (for example `linux-x86_64`, `macos-aarch64`, `android-armv8`).
3. Verify architecture locally:
  - Linux: `file libyoimiya-linux-x86_64.so`
  - macOS: `file libyoimiya-macos-x86_64.dylib` or `file libyoimiya-macos-aarch64.dylib`
4. Place the file into `platforms/<your-platform>/`.
5. Run the Python smoke test below and confirm:
  - `valid=True`
  - `bytes=164`
6. If using `yoimiya_prove_test(...)` (manual SRS), ensure witness length is always `num_constraints + 1`.

If any step fails, see the Troubleshooting section in this README first.

### ⚡ 5-Minute Device Test (Python)

```bash
cd bindings/python
python -c "import yoimiya; n=1000; w=[1]*(n+1); p=yoimiya.prove_test_precompiled(n,w); print('valid=', p.verify_precompiled(), 'bytes=', p.byte_size())"
```

Expected output:
- `valid=True`
- `bytes=164`

Notes:
- For `num_constraints = n`, witness length must be at least `n + 1`
  (equivalently: `witness_len > n`).
- `prove_test_precompiled(...)` uses bundled precompiled SRS automatically.

### 🔍 C ABI Smoke Test (NULL Pointer Guard)

Use this to quickly detect wrong binary selection or witness mismatch:

```bash
python - <<'PY'
import ctypes

lib = ctypes.CDLL('./platforms/linux-x86_64/libyoimiya-linux-x86_64.so')

class YoimiyaSrs(ctypes.Structure):
  pass

class YoimiyaProof(ctypes.Structure):
  pass

lib.yoimiya_generate_test_srs.argtypes = [ctypes.c_uint32]
lib.yoimiya_generate_test_srs.restype = ctypes.POINTER(YoimiyaSrs)

lib.yoimiya_prove_test.argtypes = [
  ctypes.c_uint32,
  ctypes.POINTER(ctypes.c_uint64),
  ctypes.c_uint32,
  ctypes.POINTER(YoimiyaSrs),
]
lib.yoimiya_prove_test.restype = ctypes.POINTER(YoimiyaProof)

lib.yoimiya_free_proof.argtypes = [ctypes.POINTER(YoimiyaProof)]
lib.yoimiya_free_srs.argtypes = [ctypes.POINTER(YoimiyaSrs)]

n = 1000
srs = lib.yoimiya_generate_test_srs(n + 1)
witness = (ctypes.c_uint64 * (n + 1))(*([1] * (n + 1)))
proof = lib.yoimiya_prove_test(n, witness, n + 1, srs)

print('proof_ptr_is_null=', not bool(proof))

if proof:
  lib.yoimiya_free_proof(proof)
lib.yoimiya_free_srs(srs)
PY
```

Expected output: `proof_ptr_is_null=False`

### 📈 Benchmark Commands (100 → 1,000,000 constraints)

Run this from the SDK root to benchmark prove/verify across small to very large circuits:

```bash
python -c "import sys,time; sys.path.insert(0,'bindings/python'); import yoimiya as y; sizes=[100,500,1000,2000,10000,50000,100000,250000,500000,1000000]; print('constraints,prove_ms,verify_ms,ok,proof_bytes');
for n in sizes:
  w=[1]*(n+1)
  t=time.perf_counter(); p=y.prove_test_precompiled(n,w); prove=(time.perf_counter()-t)*1000
  t=time.perf_counter(); ok=p.verify_precompiled(); verify=(time.perf_counter()-t)*1000
  print(f'{n},{prove:.2f},{verify:.3f},{ok},{p.byte_size()}')"
```

If you want fixed 1M telemetry (including peak memory), run:

```bash
python test_1m_only.py
```

Tip: The first touch of a new precompiled SRS tier can include one-time setup cost.
For stable numbers, run the benchmark command once as warmup, then run it again for measured timings.

---

## 📋 Quick Links

- **Check Binary Status:** [docs/RELEASE_STATUS.md](docs/RELEASE_STATUS.md)
- **Setup Guide:** [docs/GETTING_STARTED.md](docs/GETTING_STARTED.md)
- **GitHub Actions:** https://github.com/atlasw231-maker/Atlas-Yoimiya-SDK/actions
- **Releases:** https://github.com/atlasw231-maker/Atlas-Yoimiya-SDK/releases

### Structure

```
sdk/
├── platforms/          # Pre-built binaries for each platform
│   ├── windows-x86_64/
│   │   └── yoimiya-windows-x86_64.dll
│   ├── linux-x86_64/
│   │   └── libyoimiya-linux-x86_64.so
│   ├── macos-x86_64/
│   │   └── libyoimiya-macos-x86_64.dylib
│   ├── macos-aarch64/
│   │   └── libyoimiya-macos-aarch64.dylib
│   ├── android-armv8/
│   │   └── libyoimiya-android-armv8.so
│   └── ios-arm64/
│       └── libyoimiya-ios-arm64.a
├── include/            # C headers
├── bindings/           # Language-specific bindings
│   ├── python/         # Python ctypes bindings
│   ├── nodejs/         # Node.js FFI bindings
│   └── csharp/         # C# P/Invoke bindings
├── libs/               # Test utilities library
│   ├── test-utils.py
│   ├── test-utils.js
│   └── test-utils.cs
├── examples/           # Complete working examples
└── docs/               # Full documentation
```

**⚠️ Important:** Binary files (.dll, .dylib, .so, .a) must be present in their respective platform directories.

---

## ✅ Test Installation

**Quick test to verify SDK is working:**

```bash
# Python
python libs/test-utils.py

# Node.js
node libs/test-utils.js

# C#
csc Program.cs libs/test-utils.cs && Program.exe
```

**Expected:** All tests should pass (14/14).

**See [GETTING_STARTED.md](docs/GETTING_STARTED.md) for:**
- How to download binaries
- Platform-specific setup
- Building language bindings
- Running full test suite
- Testing large constraints (up to 1M)
- Troubleshooting

---

## 🚀 Installation

### Python

```bash
cd sdk/bindings/python
pip install .
```

**Usage (recommended, no manual SRS):**
```python
from yoimiya import prove_test_precompiled

num_constraints = 500
witness = [1] * (num_constraints + 1)

proof = prove_test_precompiled(num_constraints=num_constraints, witness=witness)
assert proof.verify_precompiled()
```

**Usage (explicit SRS):**
```python
from yoimiya import generate_test_srs, prove_test

num_constraints = 500
witness = [1] * (num_constraints + 1)
srs = generate_test_srs(max_degree=num_constraints + 1)

proof = prove_test(num_constraints=num_constraints, witness=witness, srs=srs)
assert proof.verify(srs)
```

### Troubleshooting (Important)

If `yoimiya_prove_test()` returns NULL or a wrapper raises `Failed to prove`, check these in order:

1. Wrong binary for your platform/arch:
  - Linux must use `libyoimiya-linux-x86_64.so`
  - macOS Intel must use `libyoimiya-macos-x86_64.dylib`
  - macOS Apple Silicon must use `libyoimiya-macos-aarch64.dylib`
2. Witness length mismatch:
  - For `num_constraints = n`, witness length must be at least `n + 1`
    (equivalently: `witness_len > n`)
3. SRS too small (manual SRS path):
  - `max_degree >= num_constraints + 1`
4. Stale binary copy:
  - Remove old `.so/.dylib/.dll` files from platform and binding folders, then copy only the intended one.

If needed, prefer the precompiled API first:
`prove_test_precompiled(...)` + `verify_precompiled(...)`

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

YoimiyaProof* proof = yoimiya_prove_test_precompiled(500, witness, len);
int valid = yoimiya_verify_precompiled(proof);  // 1 = valid, 0 = invalid
yoimiya_free_proof(proof);
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
| `precompiled_srs_degree(num_constraints)` | Get bundled SRS tier for this circuit size |
| `prove_test(constraints, witness, srs)` | Prove test circuit |
| `prove_test_precompiled(constraints, witness)` | Prove without manual SRS handle |
| `verify(proof, srs)` | Verify single proof |
| `verify_precompiled(proof)` | Verify without manual SRS handle |
| `aggregate_proofs(proofs[], srs)` | Aggregate proofs |
| `batch_proof.to_calldata()` | Serialize batch proof to 275-byte EVM calldata |

---

## 💡 Common Tasks

### Generate Proofs on Your Dev Machine

```python
# Python (fast path)
from yoimiya import prove_test_precompiled

n = 1000
witness = [1] * (n + 1)
proof = prove_test_precompiled(num_constraints=n, witness=witness)
assert proof.verify_precompiled(), "Proof failed!"
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
