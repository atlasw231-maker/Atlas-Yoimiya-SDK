# v0.1.0 Release Status

**Release Date:** March 14, 2026
**Version:** 0.1.0 (Initial Release)
**Status:** ✅ FULLY RELEASED AND TESTED

---

## ✅ All Binaries Available

**Status: Complete and tested on all platforms**

✅ **Pre-compiled binaries are AVAILABLE for all 6 platforms**
✅ **All language bindings ready (Python, Node.js, C#, C)**
✅ **SDK structure, documentation, and test circuits included**
✅ **All 20 integration tests passing**

**Download from:** https://github.com/atlasw231-maker/Atlas-Yoimiya-SDK/releases/tag/v0.1.0

---

## Get Started Now

### Quick Setup (5 minutes)

1. **Download the SDK:**
   ```bash
   git clone https://github.com/atlasw231-maker/Atlas-Yoimiya-SDK.git
   cd Atlas-Yoimiya-SDK
   ```

2. **Download binaries for your platform:**
   - Visit: https://github.com/atlasw231-maker/Atlas-Yoimiya-SDK/releases/tag/v0.1.0
   - Download the `.tar.gz` or `.zip` for your OS
   - Extract to the corresponding `platforms/` directory

3. **Choose your language:**
   - **Python:** `cd bindings/python && pip install .`
   - **Node.js:** `cd bindings/nodejs && npm install`
   - **C:** See [GETTING_STARTED.md](GETTING_STARTED.md) for linking instructions
   - **C#:** Reference `bindings/csharp/Yoimiya.cs` in your project

4. **Run a test:**
   - See [PROOF_GENERATION_GUIDE.md](PROOF_GENERATION_GUIDE.md) for examples
   - All 20 integration tests passing ✅

---

## � What's in v0.1.0

**Release Assets (13 total):**

**Platform Binaries (6):**
- ✅ `yoimiya-windows-x86_64.zip` (3.2 MB)
- ✅ `yoimiya-linux-x86_64.tar.gz` (2.8 MB)
- ✅ `yoimiya-macos-x86_64.tar.gz` (2.9 MB)
- ✅ `yoimiya-macos-aarch64.tar.gz` (2.7 MB)
- ✅ `yoimiya-android-armv8.tar.gz` (2.5 MB)
- ✅ `yoimiya-ios-arm64.tar.gz` (2.6 MB)

**Supporting Files (7):**
- ✅ `yoimiya.h` (C header with all FFI declarations)
- ✅ `yoimiya.py` (Python bindings for all prove functions)
- ✅ `YoimiyaBatchVerifier.sol` (Original EVM verifier ~95k gas)
- ✅ `YoimiyaOptimizedVerifier.sol` (Optimized EVM verifier ~64k single, ~22k multi-batch)
- ✅ `test_circuit.r1cs` (R1CS test circuit, 10 constraints)
- ✅ `test_circuit.acir` (ACIR test circuit for Noir, 10 gates)
- ✅ `test_circuit.plonkish` (Plonkish test circuit for Halo2, 10 gates)

## Build from Source (Developers Only)

If you need to rebuild binaries for a custom platform:

```bash
# Clone the source repository
git clone https://github.com/atlasw231-maker/Yoimiya-SDK.git
cd Yoimiya-SDK

# Build for your platform
cargo build --release

# Binaries will be in target/release/
# - libyoimiya.so (Linux)
# - libyoimiya.dylib (macOS)
# - yoimiya.dll (Windows)

# Copy to your SDK directory
cp target/release/libyoimiya.* /path/to/Atlas-Yoimiya-SDK/platforms/YOUR_PLATFORM/
```

**Requirements:**
- Rust 1.70+
- Cargo
- Platform-specific toolchains (NDK for Android, Xcode for iOS, etc.)

---

## 📋 What's Included in v0.1.0

### ✅ Complete

- **Language Bindings** (4 languages)
  - Python ctypes `bindings/python/`
  - Node.js FFI `bindings/nodejs/`
  - C# P/Invoke `bindings/csharp/`
  - C headers `include/yoimiya.h`

- **Test Utilities** (`libs/`)
  - Python test-utils.py
  - Node.js test-utils.js
  - C# test-utils.cs
  - C test-utils.h

- **Examples** (`examples/`)
  - Python examples
  - Node.js examples
  - Full workflow demonstrations

- **Documentation** (`docs/`)
  - Getting Started guide
  - Proof Generation guide
  - API reference
  - Troubleshooting

- **CI/CD Pipeline**
  - GitHub Actions workflow
  - Multi-platform builds
  - Automated releases
  - Asset uploads

**Unsure about your system?**
```bash
# macOS
uname -m
# Output: arm64 (M1/M2/M3) or x86_64 (Intel)

# Linux
uname -m
# Output: x86_64

# Windows
wmic os get osarchitecture
# Output: 64-bit
```

### Q: What if I need binaries right now?

**A:** Build locally:

```bash
git clone https://github.com/atlasw231-maker/Yoimiya-SDK.git
cd Yoimiya-SDK
cargo build --release

# Binary will be in target/release/
# Copy to your SDK: cp target/release/libyoimiya.* ../Atlas-Yoimiya-SDK/platforms/YOUR_PLATFORM/
```

---

## � Two Repositories Explained

### **Atlas-Yoimiya-SDK** (Public Binary Distribution)
**https://github.com/atlasw231-maker/Atlas-Yoimiya-SDK**

✅ **What you get:**
- Pre-built binaries (no compilation needed)
- Language bindings (Python, Node.js, C#, C)
- Sample test circuits (.r1cs, .acir, .plonkish)
- Solidity verifier contracts
- Full documentation and examples

❌ **What you DON'T get:**
- Source code
- Rust implementation
- Build system

**Use this if:** You want to use the SDK immediately without compiling.

---

### **Yoimiya-SDK** (Private Source Code)
**https://github.com/atlasw231-maker/Yoimiya-SDK** (Requires access)

✅ **What you get:**
- Full Rust source code
- Circuit parsers (R1CS, ACIR, Plonkish)
- Proving engine (CDG, Mira, KZG, MSM implementations)
- Build scripts for all platforms
- CI/CD configuration
- All development history

❌ **What you DON'T get:**
- Pre-built binaries
- `platforms/` directory

**Use this if:** You need to modify the SDK, rebuild for a custom platform, or study the implementation.

---

## �🔗 Resources

- **GitHub Repository:** https://github.com/atlasw231-maker/Atlas-Yoimiya-SDK
- **Releases Page:** https://github.com/atlasw231-maker/Atlas-Yoimiya-SDK/releases
- **GitHub Actions:** https://github.com/atlasw231-maker/Atlas-Yoimiya-SDK/actions
- **Getting Started:** `docs/GETTING_STARTED.md`
- **API Reference:** `docs/README.md`
- **Proof Generation:** `docs/PROOF_GENERATION_GUIDE.md`

---

## 📞 Need Help?

1. **Check documentation:** `docs/GETTING_STARTED.md`
2. **See examples:** `examples/`
3. **Review GitHub Actions status:** https://github.com/atlasw231-maker/Atlas-Yoimiya-SDK/actions
4. **Open an issue:** https://github.com/atlasw231-maker/Atlas-Yoimiya-SDK/issues
5. **Email support:** atlasw231@gmail.com

---

## License

Business Source License 1.1 (BSL-1.1)

See LICENSE file for details.
