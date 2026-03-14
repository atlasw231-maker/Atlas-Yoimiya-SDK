/**
 * Yoimiya ZK Proving SDK - Node.js Bindings
 *
 * Uses koffi for FFI — ships prebuilt binaries, no compilation required.
 * Supports Node.js 18, 20, 22, 24 on Windows/Linux/macOS.
 */

'use strict';

const koffi = require('koffi');
const path = require('path');
const os = require('os');
const fs = require('fs');

// ─── Platform detection ───────────────────────────────────────────────────────

function getLibraryPath() {
  const platform = os.platform();
  const arch = os.arch();

  const platformDirMap = {
    'win32:x64':   'windows-x86_64',
    'linux:x64':   'linux-x86_64',
    'darwin:x64':  'macos-x86_64',
    'darwin:arm64':'macos-aarch64',
  };

  const libNameMap = {
    'win32':  'yoimiya.dll',
    'linux':  'libyoimiya.so',
    'darwin': 'libyoimiya.dylib',
  };

  const libName = libNameMap[platform];
  if (!libName) throw new Error(`Unsupported platform: ${platform} ${arch}`);

  const platformDir = platformDirMap[`${platform}:${arch}`] || `${platform}-${arch}`;

  const candidates = [
    libName,
    path.join(__dirname, libName),
    path.join(__dirname, 'lib', libName),
    path.join(__dirname, '..', '..', 'platforms', platformDir, libName),
  ];

  for (const p of candidates) {
    if (fs.existsSync(p)) return path.resolve(p);
  }

  throw new Error(
    `Could not find ${libName}. Expected at platforms/${platformDir}/${libName}`
  );
}

// ─── Load library ─────────────────────────────────────────────────────────────

const lib = koffi.load(getLibraryPath());

// ─── FFI declarations ─────────────────────────────────────────────────────────
// All opaque SDK types are represented as void* (koffi external pointers).

const yoimiya_generate_test_srs  = lib.func('void* yoimiya_generate_test_srs(uint32 max_degree)');
const yoimiya_free_srs            = lib.func('void  yoimiya_free_srs(void* srs)');

const yoimiya_prove_test          = lib.func('void* yoimiya_prove_test(uint32 num_constraints, uint64* witness, uint32 witness_len, void* srs)');
const yoimiya_prove_r1cs          = lib.func('void* yoimiya_prove_r1cs(const char* path, uint64* witness, uint32 witness_len, void* srs)');
const yoimiya_prove_acir          = lib.func('void* yoimiya_prove_acir(const char* path, uint64* witness, uint32 witness_len, void* srs)');
const yoimiya_prove_plonkish      = lib.func('void* yoimiya_prove_plonkish(const char* path, uint64* witness, uint32 witness_len, void* srs)');
const yoimiya_free_proof          = lib.func('void  yoimiya_free_proof(void* proof)');
const yoimiya_proof_size_bytes    = lib.func('int32 yoimiya_proof_size_bytes(void* proof)');

// Both Proof and BatchProof are verified through the same yoimiya_verify entry point
const yoimiya_verify              = lib.func('int32 yoimiya_verify(void* proof, void* srs)');

const yoimiya_aggregate           = lib.func('void* yoimiya_aggregate(void** proofs, uint32 count, void* srs)');
const yoimiya_free_batch_proof    = lib.func('void  yoimiya_free_batch_proof(void* batch)');
const yoimiya_batch_to_calldata   = lib.func('int32 yoimiya_batch_to_calldata(void* batch, uint8* out, uint32 out_len)');

// ─── Helpers ──────────────────────────────────────────────────────────────────

function toWitnessBuffer(witness) {
  const buf = new BigUint64Array(witness.length);
  for (let i = 0; i < witness.length; i++) buf[i] = BigInt(witness[i]);
  return buf;
}

function toPtrArray(handles) {
  // Build a BigUint64Array of pointer addresses for void**
  const addrs = new BigUint64Array(handles.length);
  for (let i = 0; i < handles.length; i++) {
    addrs[i] = koffi.address(handles[i]);
  }
  return addrs;
}

// ─── Wrapper classes ──────────────────────────────────────────────────────────

class Srs {
  constructor(maxDegree) {
    this.handle = yoimiya_generate_test_srs(maxDegree);
    if (!this.handle) throw new Error('Failed to generate SRS');
  }
  destroy() {
    if (this.handle) { yoimiya_free_srs(this.handle); this.handle = null; }
  }
}

class Proof {
  constructor(handle) { this.handle = handle; }

  verify(srs) {
    const r = yoimiya_verify(this.handle, srs.handle);
    if (r === -1) throw new Error('Verification error');
    return r === 1;
  }

  byteSize() {
    const s = yoimiya_proof_size_bytes(this.handle);
    if (s < 0) throw new Error('Failed to get proof byte size');
    return s;
  }

  destroy() {
    if (this.handle) { yoimiya_free_proof(this.handle); this.handle = null; }
  }
}

class BatchProof {
  constructor(handle) { this.handle = handle; }

  verify(srs) {
    // BatchProof is verified through the same yoimiya_verify entry point as Proof
    const r = yoimiya_verify(this.handle, srs.handle);
    if (r === -1) throw new Error('Batch verification error');
    return r === 1;
  }

  toCalldata() {
    const out = Buffer.alloc(275);
    const written = yoimiya_batch_to_calldata(this.handle, out, 275);
    if (written < 0) throw new Error('Failed to serialize batch proof');
    return out.subarray(0, written);
  }

  destroy() {
    if (this.handle) { yoimiya_free_batch_proof(this.handle); this.handle = null; }
  }
}

// ─── Public API ───────────────────────────────────────────────────────────────

function generateTestSrs(maxDegree) {
  return new Srs(maxDegree);
}

function proveTest(numConstraints, witness, srs) {
  if (witness.length < numConstraints + 1) {
    throw new Error(
      `witness too short: got ${witness.length}, need at least ${numConstraints + 1}`
    );
  }
  const handle = yoimiya_prove_test(
    numConstraints, toWitnessBuffer(witness), witness.length, srs.handle
  );
  if (!handle) throw new Error('Failed to prove');
  return new Proof(handle);
}

function proveR1cs(r1csPath, witness, srs) {
  const handle = yoimiya_prove_r1cs(
    r1csPath, toWitnessBuffer(witness), witness.length, srs.handle
  );
  if (!handle) throw new Error('Failed to prove R1CS');
  return new Proof(handle);
}

function aggregateProofs(proofs, srs) {
  if (proofs.length === 0) throw new Error('No proofs to aggregate');
  const ptrArr = toPtrArray(proofs.map(p => p.handle));
  const handle = yoimiya_aggregate(ptrArr, proofs.length, srs.handle);
  if (!handle) throw new Error('Failed to aggregate proofs');
  return new BatchProof(handle);
}

module.exports = { Srs, Proof, BatchProof, generateTestSrs, proveTest, proveR1cs, aggregateProofs };
