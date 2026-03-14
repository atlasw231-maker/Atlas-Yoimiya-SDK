/**
 * Preinstall helper: verify that the platform binary is present.
 *
 * This script does NOT download anything automatically — the Yoimiya SDK
 * distributes pre-built binaries through the repository itself (platforms/).
 * If the binary is missing, it prints a clear error pointing to the release page.
 */

'use strict';

const path = require('path');
const fs   = require('fs');
const os   = require('os');

const platform = os.platform();
const arch     = os.arch();

const platformDirMap = {
  'win32:x64':    'windows-x86_64',
  'linux:x64':    'linux-x86_64',
  'darwin:x64':   'macos-x86_64',
  'darwin:arm64': 'macos-aarch64',
};

const libNameMap = {
  'win32':  'yoimiya.dll',
  'linux':  'libyoimiya.so',
  'darwin': 'libyoimiya.dylib',
};

const libName    = libNameMap[platform];
const platformDir = platformDirMap[`${platform}:${arch}`];

if (!libName || !platformDir) {
  // Unknown platform — skip the check; runtime will fail with a clear message.
  process.exit(0);
}

const sdkRoot  = path.resolve(__dirname, '..', '..', '..');
const libPath  = path.join(sdkRoot, 'platforms', platformDir, libName);

if (!fs.existsSync(libPath)) {
  console.warn(`
[yoimiya-sdk] WARNING: platform binary not found at:
  ${libPath}

If you cloned the repository, make sure you are on the correct branch/tag.
If you need the pre-built binary, download it from:
  https://github.com/atlasw231-maker/Atlas-Yoimiya-SDK/releases/tag/v0.1.0

The install will succeed without the binary, but require() will fail at runtime
until the file is present.
`);
} else {
  const stat = fs.statSync(libPath);
  console.log(`[yoimiya-sdk] Found ${platformDir}/${libName} (${(stat.size / 1024 / 1024).toFixed(1)} MB)`);
}
