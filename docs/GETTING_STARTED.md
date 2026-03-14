# Getting Started: Download & Test Yoimiya Binary SDK

**Step-by-step guide to download pre-built binaries and test the SDK on your platform.**

---

## Overview

The Yoimiya SDK is distributed as **pre-compiled binaries only**. There's no source code to build—you simply download the binaries for your platform and start using them.

### What You Get

✅ Pre-compiled binary libraries (.dll, .dylib, .so)
✅ Language bindings (Python, Node.js, C#, C)
✅ Test utilities and examples
✅ Complete documentation

---

## ✅ Binaries Available Now

**All pre-compiled binaries are published and ready for download!**

**Current Status:**
- ✅ SDK structure, bindings, tests, documentation ready
- ✅ All pre-compiled binaries published and tested
- ✅ All 6 platforms available (Windows, Linux, macOS Intel/Apple Silicon, Android, iOS)
- ✅ 13 total release assets including headers, Python bindings, and test circuits

**Version:** v0.1.0 (March 2026)
**Test Status:** All 20 integration tests passing

---

## Step 1: Download the SDK

### Option A: Using GitHub Releases (Recommended)

**Prerequisites:** Git or manual download capability

1. Go to: https://github.com/atlasw231-maker/Atlas-Yoimiya-SDK/releases/tag/v0.1.0

2. **Download SDK structure:**
   - Via git clone OR
   - Download source code ZIP/TAR.GZ

3. **Download platform-specific binaries:**
   - Look under "Assets" section for your platform:
   - `yoimiya-windows-x86_64.zip` (Windows)
   - `yoimiya-macos-x86_64.tar.gz` (macOS Intel)
   - `yoimiya-macos-aarch64.tar.gz` (macOS Apple Silicon)
   - `yoimiya-linux-x86_64.tar.gz` (Linux)
   - `yoimiya-android-armv8.tar.gz` (Android)
   - `yoimiya-ios-arm64.tar.gz` (iOS)

4. Extract the SDK structure:
   ```bash
   # macOS/Linux
   tar -xzf Atlas-Yoimiya-SDK-v0.1.0.tar.gz
   cd Atlas-Yoimiya-SDK
   
   # Windows (using PowerShell)
   Expand-Archive Atlas-Yoimiya-SDK-v0.1.0.zip
   cd Atlas-Yoimiya-SDK
   ```

5. Extract your platform's binaries into the correct directory:
   ```bash
   # Example: macOS x86_64
   tar -xzf yoimiya-macos-x86_64.tar.gz -C platforms/macos-x86_64/
   
   # Example: Linux
   tar -xzf yoimiya-linux-x86_64.tar.gz -C platforms/linux-x86_64/
   
   # Example: Windows
   Expand-Archive yoimiya-windows-x86_64.zip -DestinationPath platforms/windows-x86_64/
   ```

### Option B: Clone the Repository

```bash
git clone https://github.com/atlasw231-maker/Atlas-Yoimiya-SDK.git
cd Atlas-Yoimiya-SDK
git checkout v0.1.0
```

---

## Step 2: Locate Your Platform Binaries

After extraction, navigate to the `platforms/` directory:

```
yoimiya-sdk-v0.1.0/
├── platforms/
│   ├── windows-x86_64/
│   │   └── yoimiya.dll         ← Windows binary
│   ├── linux-x86_64/
│   │   └── libyoimiya.so       ← Linux binary
│   ├── macos-x86_64/
│   │   └── libyoimiya.dylib    ← Intel macOS binary
│   ├── macos-aarch64/
│   │   └── libyoimiya.dylib    ← Apple Silicon macOS binary
│   ├── android-armv8/
│   │   └── libyoimiya.so       ← Android binary
│   └── ios-arm64/
│       └── libyoimiya.dylib    ← iOS binary
├── include/
│   └── yoimiya.h               ← C header
├── bindings/
│   ├── python/                 ← Python bindings
│   ├── nodejs/                 ← Node.js bindings
│   └── csharp/                 ← C# bindings
├── libs/
│   ├── test-utils.py           ← Python test library
│   ├── test-utils.js           ← Node.js test library
│   └── test-utils.cs           ← C# test library
├── examples/
│   ├── proof_generation_guide.py
│   ├── proof_generation_guide.js
│   └── python_example.py
├── docs/
│   └── PROOF_GENERATION_GUIDE.md
└── README.md
```

### ⚠️ Important: Binary Location

**Your platform's binary must be in the corresponding `platforms/` subdirectory:**

- **Windows:** `platforms/windows-x86_64/yoimiya.dll`
- **macOS Intel:** `platforms/macos-x86_64/libyoimiya.dylib`
- **macOS Apple Silicon:** `platforms/macos-aarch64/libyoimiya.dylib`
- **Linux:** `platforms/linux-x86_64/libyoimiya.so`

If the binary files are empty or missing, the GitHub release hasn't been built yet. Contact support or check the releases page for the latest available binary release.

---

## Step 3: Verify Binary Installation

### Verify Binary Files Exist

**Windows (PowerShell):**
```powershell
# Check if DLL exists and has content
Get-Item .\platforms\windows-x86_64\yoimiya.dll | Select-Object FullName, Length

# Output should show file size > 0
```

**macOS/Linux:**
```bash
# Check if library exists and has content
ls -lh platforms/macos-x86_64/libyoimiya.dylib
# or
ls -lh platforms/linux-x86_64/libyoimiya.so

# Output should show file size > 0 (e.g., 5.2M, not 0 bytes)
```

### If Files Are Empty or Missing

**Problem:** You see the directory but the binary file is empty (0 bytes) or doesn't exist.

**Solution:** Re-download from GitHub Releases

1. Go to: https://github.com/atlasw231-maker/Atlas-Yoimiya-SDK/releases/tag/v0.1.0
2. Under "Assets", download the correct archive for your OS:
   - `yoimiya-windows-x86_64.zip` (Windows x86_64)
   - `yoimiya-linux-x86_64.tar.gz` (Linux x86_64)
   - `yoimiya-macos-x86_64.tar.gz` (macOS Intel)
   - `yoimiya-macos-aarch64.tar.gz` (macOS Apple Silicon)
   - `yoimiya-android-armv8.tar.gz` (Android ARMv8)
   - `yoimiya-ios-arm64.tar.gz` (iOS ARM64)
3. Extract and verify the binary size (should be several MB, not empty)

---

## Step 4: Set Up Language Bindings

Choose your language and follow the setup:

### 4A: Python Setup

1. **Verify Python version:**
   ```bash
   python --version  # Should be 3.7+
   ```

2. **Install bindings:**
   ```bash
   cd bindings/python
   pip install .
   ```

3. **Test installation:**
   ```bash
   python -c "from yoimiya import generateTestSrs; print('✓ Python bindings working!')"
   ```

### 4B: Node.js Setup

1. **Verify Node version:**
   ```bash
   node --version  # Should be 14+
   ```

2. **Install bindings:**
   ```bash
   cd bindings/nodejs
   npm install
   ```

3. **Test installation:**
   ```bash
   node -e "const y = require('./index.js'); console.log('✓ Node.js bindings working!')"
   ```

### 4C: C# Setup

1. **Add reference to `Yoimiya.cs`:**
   ```csharp
   // In your project
   #r "path/to/bindings/csharp/Yoimiya.cs"
   using Yoimiya.SDK;
   ```

2. **Test:**
   ```csharp
   var sdk = new YoimiyaSdk();
   Console.WriteLine("✓ C# bindings working!");
   ```

### 4D: C Setup

1. **Compiler requirements:**
   - GCC/Clang on Linux/macOS
   - MSVC/MinGW on Windows

2. **Include header:**
   ```c
   #include "include/yoimiya.h"
   ```

3. **Link library:**
   ```bash
   # Linux
   gcc -o myapp myapp.c -I./include -L./platforms/linux-x86_64 -lyoimiya
   
   # macOS Intel
   gcc -o myapp myapp.c -I./include -L./platforms/macos-x86_64 -lyoimiya
   
   # macOS Apple Silicon
   gcc -o myapp myapp.c -I./include -L./platforms/macos-aarch64 -lyoimiya
   
   # Windows (MSVC)
   cl myapp.c /I.\include /link /LIBPATH:.\platforms\windows-x86_64 yoimiya.lib
   ```

---

## Step 5: Run Tests

### 5A: Quick Sanity Check

**Python:**
```bash
python -c "from libs.test_utils import quick_test; quick_test()"
```

**Node.js:**
```bash
node -e "const {quickTest} = require('./libs/test-utils.js'); quickTest();"
```

**C#:**
```csharp
using Yoimiya.TestUtils;
QuickTest.Run();
```

### 5B: Run Test Suite

**Python:**
```bash
python libs/test-utils.py
```

**Node.js:**
```bash
node libs/test-utils.js
```

**C#:**
```bash
csc Program.cs libs/test-utils.cs && Program.exe
```

### Expected Output

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

### 5C: Test Large Constraints (Up to 1M)

**Python:**
```python
from libs.test_utils import YoimiyaTester

tester = YoimiyaTester(max_degree=1_000_000)
results = tester.test_large_constraints([
    10_000, 50_000, 100_000, 250_000, 500_000, 1_000_000
])
```

**Expected output:**
```
Testing Large Constraint Sizes (up to 1M)...
------------------------------------------------------------
  Testing 10,000 constraints... ✓ Prove: 3.2145ms, Verify: 0.8923ms
  Testing 50,000 constraints... ✓ Prove: 15.8234ms, Verify: 0.9102ms
  Testing 100,000 constraints... ✓ Prove: 31.2450ms, Verify: 0.9234ms
  Testing 250,000 constraints... ✓ Prove: 80.1234ms, Verify: 0.9567ms
  Testing 500,000 constraints... ✓ Prove: 162.4567ms, Verify: 0.9876ms
  Testing 1,000,000 constraints... ✓ Prove: 331.2345ms, Verify: 1.0123ms
```

---

## Step 6: Test with Your Own Code

### Python Example

```python
from yoimiya import generate_test_srs, prove_test

# Initialize
srs = generate_test_srs(max_degree=2048)
print("✓ SRS generated")

# Generate proof
witness = [1, 2, 3, 4]
proof = prove_test(
    num_constraints=500,
    witness=witness,
    srs=srs
)
print("✓ Proof generated")

# Verify
is_valid = proof.verify(srs)
print(f"✓ Proof valid: {is_valid}")
```

### Node.js Example

```javascript
const { generateTestSrs, proveTest } = require('./bindings/nodejs');

// Initialize
const srs = generateTestSrs(2048);
console.log("✓ SRS generated");

// Generate proof
const witness = [1n, 2n, 3n, 4n];
const proof = proveTest(500, witness, srs);
console.log("✓ Proof generated");

// Verify
const isValid = proof.verify(srs);
console.log(`✓ Proof valid: ${isValid}`);
```

### C Example

```c
#include "yoimiya.h"
#include <stdio.h>

int main() {
    // Initialize
    YoimiyaSrs* srs = yoimiya_generate_test_srs(2048);
    printf("✓ SRS generated\n");
    
    // Generate proof
    uint8_t witness[] = {1, 2, 3, 4};
    YoimiyaProof* proof = yoimiya_prove_test(500, witness, 4, srs);
    printf("✓ Proof generated\n");
    
    // Verify
    int valid = yoimiya_verify(proof, srs);
    printf("✓ Proof valid: %d\n", valid);
    
    // Cleanup
    yoimiya_free_proof(proof);
    yoimiya_free_srs(srs);
    
    return 0;
}
```

---

## Troubleshooting

### Issue: "Cannot find binary" or "DLL not found"

**Cause:** Binary file is not in the correct location

**Solution:**
1. Verify binary exists: `ls -la platforms/YOUR_PLATFORM/`
2. Verify file size > 0: `ls -lh platforms/YOUR_PLATFORM/libyoimiya.*`
3. If empty, download from GitHub releases
4. Ensure correct platform directory:
   - Windows: `windows-x86_64/`
   - macOS Intel: `macos-x86_64/`
   - macOS ARM: `macos-aarch64/`
   - Linux: `linux-x86_64/`

### Issue: "Module not found" (Python)

**Cause:** Python bindings not installed

**Solution:**
```bash
cd bindings/python
pip install .  # Install in editable mode
pip install -e .  # Or like this
```

### Issue: "Cannot find module" (Node.js)

**Cause:** Node.js bindings not set up

**Solution:**
```bash
cd bindings/nodejs
npm install  # Install dependencies
# Verify it works
node -e "require('./index.js')"
```

### Issue: Tests fail with "SRS generation error"

**Cause:** Binary is corrupted or incompatible with your system

**Solution:**
1. Re-download binary from GitHub releases
2. Verify SHA256 checksum if provided
3. Verify your system matches the platform:
   - `uname -m` (Linux/macOS) → should match directory
   - Check architecture: Intel vs ARM

### Issue: Proof generation is very slow

**Cause:** Running on wrong OS or CPU limitations

**Solution:**
1. Verify you're using the correct binary for your platform
2. Check system CPU usage: `top` (macOS/Linux) or Task Manager (Windows)
3. Close other applications using CPU
4. Run on a more powerful machine for large constraints

---

## Verification Checklist

After following all steps, verify:

- [ ] Binary files exist in `platforms/YOUR_PLATFORM/`
- [ ] Binary files are not 0 bytes (have real content)
- [ ] Language bindings installed without errors
- [ ] Quick sanity check passes
- [ ] Full test suite passes (14/14 tests)
- [ ] Large constraint tests pass (up to 1M)
- [ ] Your own code example runs successfully

---

## What's Next?

1. **Proof Generation:** See [PROOF_GENERATION_GUIDE.md](../docs/PROOF_GENERATION_GUIDE.md)
2. **Integration:** See language-specific examples:
   - Python: `examples/python_example.py`
   - Node.js: `examples/nodejs_example.js`
3. **Testing:** See `libs/README.md` for test utilities API
4. **API Reference:** See `docs/README.md` for complete documentation

---

## Support

**Issues?**
1. Check this guide's Troubleshooting section
2. Run `libs/test-utils.py` (or .js/.cs) to verify installation
3. See `docs/PROOF_GENERATION_GUIDE.md` for detailed examples
4. Open issue on GitHub: https://github.com/atlasw231-maker/Atlas-Yoimiya-SDK/issues

---

## License

Business Source License 1.1 (BSL-1.1)

See LICENSE file for details.
