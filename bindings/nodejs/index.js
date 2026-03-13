/**
 * Yoimiya ZK Proving SDK - Node.js Bindings
 *
 * This module provides JavaScript/TypeScript bindings to the Yoimiya library.
 */

const ffi = require('ffi-napi');
const ref = require('ref-napi');
const Struct = require('ref-struct-di')(ref);
const ArrayType = require('ref-array-di')(ref);
const path = require('path');
const os = require('os');
const fs = require('fs');

// Platform detection
function getLibraryPath() {
  const platform = os.platform();
  const arch = os.arch();
  const platformDirMap = {
    'win32:x64': 'windows-x86_64',
    'linux:x64': 'linux-x86_64',
    'darwin:x64': 'macos-x86_64',
    'darwin:arm64': 'macos-aarch64',
  };
  
  const libMap = {
    'win32': 'yoimiya.dll',
    'linux': 'libyoimiya.so',
    'darwin': 'libyoimiya.dylib',
  };
  
  const libName = libMap[platform];
  if (!libName) {
    throw new Error(`Unsupported platform: ${platform} ${arch}`);
  }
  
  const searchPaths = [
    libName,
    path.join(__dirname, libName),
    path.join(__dirname, 'lib', libName),
    path.join(__dirname, '..', '..', 'platforms', platformDirMap[`${platform}:${arch}`] || `${platform}-${arch}`, libName),
  ];
  
  for (const searchPath of searchPaths) {
    if (fs.existsSync(searchPath)) {
      return path.resolve(searchPath);
    }
  }
  
  throw new Error(`Could not find Yoimiya library: ${libName}`);
}

const libPath = getLibraryPath();

// Define opaque types
const YoimiyaSrs = ref.types.void;
const YoimiyaProof = ref.types.void;
const YoimiyaBatchProof = ref.types.void;

const YoimiyaSrsPtr = ref.refType(YoimiyaSrs);
const YoimiyaProofPtr = ref.refType(YoimiyaProof);
const YoimiyaBatchProofPtr = ref.refType(YoimiyaBatchProof);
const YoimiyaProofPtrPtr = ref.refType(YoimiyaProofPtr);

// Load library
const lib = ffi.Library(libPath, {
  // SRS
  'yoimiya_generate_test_srs': [YoimiyaSrsPtr, ['uint32']],
  'yoimiya_free_srs': ['void', [YoimiyaSrsPtr]],
  
  // Proving
  'yoimiya_prove_test': [YoimiyaProofPtr, ['uint32', ref.refType(ref.types.uint64), 'uint32', YoimiyaSrsPtr]],
  'yoimiya_prove_r1cs': [YoimiyaProofPtr, ['string', ref.refType(ref.types.uint64), 'uint32', YoimiyaSrsPtr]],
  'yoimiya_free_proof': ['void', [YoimiyaProofPtr]],
  'yoimiya_proof_size_bytes': ['int32', [YoimiyaProofPtr]],
  
  // Verification
  'yoimiya_verify': ['int32', [YoimiyaProofPtr, YoimiyaSrsPtr]],
  
  // Aggregation
  'yoimiya_aggregate': [YoimiyaBatchProofPtr, [YoimiyaProofPtrPtr, 'uint32', YoimiyaSrsPtr]],
  'yoimiya_free_batch_proof': ['void', [YoimiyaBatchProofPtr]],
  'yoimiya_verify_batch': ['int32', [YoimiyaBatchProofPtr, YoimiyaSrsPtr]],
  'yoimiya_batch_to_calldata': ['int32', [YoimiyaBatchProofPtr, ref.refType(ref.types.uint8), 'uint32']],
});

// Wrapper classes
class Srs {
  constructor(maxDegree) {
    this.handle = lib.yoimiya_generate_test_srs(maxDegree);
    if (this.handle.isNull()) {
      throw new Error('Failed to generate SRS');
    }
  }
  
  destroy() {
    if (this.handle && !this.handle.isNull()) {
      lib.yoimiya_free_srs(this.handle);
    }
  }
}

class Proof {
  constructor(handle) {
    this.handle = handle;
  }
  
  verify(srs) {
    const result = lib.yoimiya_verify(this.handle, srs.handle);
    if (result === -1) {
      throw new Error('Verification error');
    }
    return result === 1;
  }

  byteSize() {
    const size = lib.yoimiya_proof_size_bytes(this.handle);
    if (size < 0) {
      throw new Error('Failed to get proof byte size');
    }
    return size;
  }
  
  destroy() {
    if (this.handle && !this.handle.isNull()) {
      lib.yoimiya_free_proof(this.handle);
    }
  }
}

class BatchProof {
  constructor(handle) {
    this.handle = handle;
  }
  
  verify(srs) {
    const result = lib.yoimiya_verify_batch(this.handle, srs.handle);
    if (result === -1) {
      throw new Error('Batch verification error');
    }
    return result === 1;
  }

  toCalldata() {
    const buffer = Buffer.alloc(275);
    const written = lib.yoimiya_batch_to_calldata(this.handle, buffer, 275);
    if (written < 0) {
      throw new Error('Failed to serialize batch proof');
    }
    return buffer.subarray(0, written);
  }
  
  destroy() {
    if (this.handle && !this.handle.isNull()) {
      lib.yoimiya_free_batch_proof(this.handle);
    }
  }
}

// Public API
function generateTestSrs(maxDegree) {
  return new Srs(maxDegree);
}

function proveTest(numConstraints, witness, srs) {
  if (witness.length < (numConstraints + 1)) {
    throw new Error(`witness too short: got ${witness.length}, need at least ${numConstraints + 1} for numConstraints=${numConstraints}`);
  }

  const witnessArray = Buffer.allocUnsafe(witness.length * 8);
  for (let i = 0; i < witness.length; i++) {
    witnessArray.writeBigUInt64LE(BigInt(witness[i]), i * 8);
  }
  
  const proofHandle = lib.yoimiya_prove_test(
    numConstraints,
    ref.cast(witnessArray, ref.refType(ref.types.uint64)),
    witness.length,
    srs.handle
  );
  
  if (proofHandle.isNull()) {
    throw new Error('Failed to prove');
  }
  
  return new Proof(proofHandle);
}

function proveR1cs(r1csPath, witness, srs) {
  const witnessArray = Buffer.allocUnsafe(witness.length * 8);
  for (let i = 0; i < witness.length; i++) {
    witnessArray.writeBigUInt64LE(BigInt(witness[i]), i * 8);
  }
  
  const proofHandle = lib.yoimiya_prove_r1cs(
    r1csPath,
    ref.cast(witnessArray, ref.refType(ref.types.uint64)),
    witness.length,
    srs.handle
  );
  
  if (proofHandle.isNull()) {
    throw new Error('Failed to prove R1CS');
  }
  
  return new Proof(proofHandle);
}

function aggregateProofs(proofs, srs) {
  if (proofs.length === 0) {
    throw new Error('No proofs to aggregate');
  }
  
  const proofHandles = Buffer.allocUnsafe(proofs.length * ref.sizeof(YoimiyaProofPtr));
  for (let i = 0; i < proofs.length; i++) {
    proofHandles.writePointer(proofs[i].handle, i * ref.sizeof(YoimiyaProofPtr));
  }
  
  const batchHandle = lib.yoimiya_aggregate(
    ref.cast(proofHandles, YoimiyaProofPtrPtr),
    proofs.length,
    srs.handle
  );
  
  if (batchHandle.isNull()) {
    throw new Error('Failed to aggregate proofs');
  }
  
  return new BatchProof(batchHandle);
}

module.exports = {
  Srs,
  Proof,
  BatchProof,
  generateTestSrs,
  proveTest,
  proveR1cs,
  aggregateProofs,
};
