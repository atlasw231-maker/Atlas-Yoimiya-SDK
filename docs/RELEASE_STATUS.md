# v0.1.0 Release Status

**Release Date:** March 2026
**Version:** 0.1.0 (Initial Release)

---

## 📦 Binary Distribution Status

### Current Status: Pre-Release (Binaries Building)

The Atlas-Yoimiya-SDK v0.1.0 is in **pre-release** with binaries currently being built by GitHub Actions CI/CD.

**What's Available Now:**
- ✅ SDK structure and all language bindings
- ✅ Test utilities library
- ✅ Documentation and examples
- ✅ C headers for native integration
- ⏳ Pre-compiled binaries (building via CI/CD)

**Expected Timeline:**
- GitHub Actions CI/CD workflow builds binaries for all 6 platforms
- Binaries uploaded to GitHub Releases as release assets
- Process takes approximately 30-60 minutes per platform

---

## 🔄 Getting Binaries

### Option 1: Download Pre-Built Binaries (When Available)

Once GitHub Actions completes, binaries will be available as release assets:

1. Go to: https://github.com/atlasw231-maker/Atlas-Yoimiya-SDK/releases/tag/v0.1.0
2. Under "Assets" section, download binaries for your platform
3. Extract to corresponding `platforms/` directory

**Platform Asset Names:**
- `yoimiya-windows-x86_64.zip` → Extract to `platforms/windows-x86_64/`
- `yoimiya-linux-x86_64.tar.gz` → Extract to `platforms/linux-x86_64/`
- `yoimiya-macos-x86_64.tar.gz` → Extract to `platforms/macos-x86_64/`
- `yoimiya-macos-aarch64.tar.gz` → Extract to `platforms/macos-aarch64/`
- `yoimiya-android-armv8.tar.gz` → Extract to `platforms/android-armv8/`
- `yoimiya-ios-arm64.tar.gz` → Extract to `platforms/ios-arm64/`

### Option 2: Monitor GitHub Actions

**Track binary build progress:**

1. Go to: https://github.com/atlasw231-maker/Atlas-Yoimiya-SDK/actions
2. Check the release.yml workflow for compilation status
3. View individual platform build logs

**Workflow Summary:**
```
Build Matrix:
├── Windows x86_64 (MSVC)
├── Linux x86_64 (GCC)
├── macOS x86_64 (Intel Clang)
├── macOS ARM64 (Apple Silicon Clang)
├── Android ARMv8 (NDK)
└── iOS ARM64 (Xcode)

Each platform builds independently and uploads to release assets
Entire process: ~30-60 minutes
```

### Option 3: Build Locally from Source

If binaries are not yet available and you need them immediately:

```bash
# Clone original source repository
git clone https://github.com/atlasw231-maker/Yoimiya-SDK.git
cd Yoimiya-SDK

# Build for your platform
cargo build --release

# Binaries will be in target/release/
```

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

### ⏳ In Progress (Via CI/CD)

- Pre-compiled binaries for 6 platforms
- Published packages:
  - PyPI (Python)
  - npm (Node.js)
  - NuGet (C#)

---

## 🚀 How to Use Right Now

### 1. Clone/Download SDK Structure

```bash
git clone https://github.com/atlasw231-maker/Atlas-Yoimiya-SDK.git
cd Atlas-Yoimiya-SDK
```

### 2. Wait for Binaries

Monitor the GitHub Actions workflow:
- https://github.com/atlasw231-maker/Atlas-Yoimiya-SDK/actions
- Estimated time: 30-60 minutes

### 3. Download Binaries (Once Available)

Check GitHub Releases > Assets:
- https://github.com/atlasw231-maker/Atlas-Yoimiya-SDK/releases/tag/v0.1.0

### 4. Extract to Platform Directory

```bash
# Example: macOS x86_64
tar -xzf yoimiya-macos-x86_64.tar.gz
# Contents go to platforms/macos-x86_64/
```

### 5. Install Language Bindings

```bash
# Python
cd bindings/python && pip install .

# Node.js
cd bindings/nodejs && npm install

# C# / C
# See GETTING_STARTED.md
```

### 6. Run Tests

```bash
# Quick test
python libs/test-utils.py

# See all tests pass
node libs/test-utils.js

# Custom code
python examples/proof_generation_guide.py
```

---

## ⏱️ Binary Availability Timeline

| Time | Event | Status |
|------|-------|--------|
| T+0 | GitHub Actions triggered | ⏳ In Progress |
| T+5-10 min | Windows build completes | ⏳ In Progress |
| T+10-20 min | Linux build completes | ⏳ In Progress |
| T+20-30 min | macOS x86_64 build completes | ⏳ In Progress |
| T+30-40 min | macOS ARM64 build completes | ⏳ In Progress |
| T+40-50 min | Android build completes | ⏳ In Progress |
| T+50-60 min | iOS build completes | ⏳ In Progress |
| T+60+ min | All assets available in GitHub Releases | ⏳ Will Update |

**Note:** Times are estimates. Check GitHub Actions for actual progress.

---

## ❓ FAQ

### Q: Why aren't binaries included in git?

**A:** Binary files are large (~5-10 MB each) and would bloat the repository. Instead:
- GitHub Actions builds them automatically
- Binaries are uploaded as release assets
- Developers download only the binaries for their platform

### Q: Can I test without binaries?

**A:** Not yet. You need the platform binary for your language bindings to work. Options:
1. Wait for GitHub Actions to complete (30-60 min)
2. Build locally from source (see Option 3 above)
3. Check back in ~1 hour for release assets

### Q: What if the build fails?

**A:** Check GitHub Actions logs:
- Go to: https://github.com/atlasw231-maker/Atlas-Yoimiya-SDK/actions
- Click on the failed workflow
- Review error messages in the logs
- Open an issue if you find a problem

### Q: Which binary should I download?

**A:** Choose based on your platform:

| Platform | Binary | CPU |
|----------|--------|-----|
| Windows | `yoimiya-windows-x86_64.zip` | Intel/AMD 64-bit |
| macOS | `yoimiya-macos-x86_64.tar.gz` | Intel Macs |
| macOS | `yoimiya-macos-aarch64.tar.gz` | Apple Silicon (M1/M2/M3) |
| Linux | `yoimiya-linux-x86_64.tar.gz` | Intel/AMD 64-bit |
| Android | `yoimiya-android-armv8.tar.gz` | ARM64 devices |
| iOS | `yoimiya-ios-arm64.tar.gz` | ARM64 devices |

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

## 🔗 Resources

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
