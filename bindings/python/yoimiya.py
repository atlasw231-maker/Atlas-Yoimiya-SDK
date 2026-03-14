"""
Yoimiya ZK Proving SDK - Python Bindings

This module provides Python bindings to the Yoimiya ZK proving library using ctypes.
"""

import ctypes
import os
import platform
from typing import Optional, List, Tuple
from pathlib import Path

# Determine library path based on platform
def _find_library() -> Optional[str]:
    """Find and return the path to the Yoimiya library."""
    system = platform.system()
    machine = platform.machine()
    
    lib_names = {
        ("Windows", "AMD64"): "yoimiya.dll",
        ("Linux", "x86_64"): "libyoimiya.so",
        ("Darwin", "x86_64"): "libyoimiya.dylib",
        ("Darwin", "arm64"): "libyoimiya.dylib",
    }
    
    lib_name = lib_names.get((system, machine))
    if not lib_name:
        raise RuntimeError(f"Unsupported platform: {system} {machine}")
    
    # Try multiple search paths
    # Derive platform dir name used in the binary SDK layout
    platform_map = {
        ("Windows", "AMD64"): "windows-x86_64",
        ("Linux", "x86_64"): "linux-x86_64",
        ("Darwin", "x86_64"): "macos-x86_64",
        ("Darwin", "arm64"): "macos-aarch64",
    }
    platform_dir = platform_map.get((system, machine), f"{system.lower()}-{machine}")
    sdk_root = Path(__file__).parent.parent.parent

    search_paths = [
        lib_name,
        f"./lib/{lib_name}",
        sdk_root / "platforms" / platform_dir / lib_name,
        Path(__file__).parent / lib_name,
    ]
    
    for path in search_paths:
        if isinstance(path, Path):
            path = str(path)
        if os.path.exists(path):
            return os.path.abspath(path)
    
    raise FileNotFoundError(f"Could not find Yoimiya library: {lib_name}")

# Load the library
_lib_path = _find_library()
_lib = ctypes.CDLL(_lib_path)

# ──────────────────────────────────────────────────────────────────
# Type Definitions
# ──────────────────────────────────────────────────────────────────

class YoimiyaSrs(ctypes.Structure):
    """Opaque SRS handle."""
    pass

class YoimiyaProof(ctypes.Structure):
    """Opaque Proof handle."""
    pass

class YoimiyaBatchProof(ctypes.Structure):
    """Opaque Batch Proof handle."""
    pass

# ──────────────────────────────────────────────────────────────────
# Function Bindings
# ──────────────────────────────────────────────────────────────────

# SRS Management
_lib.yoimiya_generate_test_srs.argtypes = [ctypes.c_uint32]
_lib.yoimiya_generate_test_srs.restype = ctypes.POINTER(YoimiyaSrs)

_lib.yoimiya_free_srs.argtypes = [ctypes.POINTER(YoimiyaSrs)]
_lib.yoimiya_free_srs.restype = None

# Proving
_lib.yoimiya_prove_test.argtypes = [
    ctypes.c_uint32,
    ctypes.POINTER(ctypes.c_uint64),
    ctypes.c_uint32,
    ctypes.POINTER(YoimiyaSrs)
]
_lib.yoimiya_prove_test.restype = ctypes.POINTER(YoimiyaProof)

_lib.yoimiya_prove_test_precompiled.argtypes = [
    ctypes.c_uint32,
    ctypes.POINTER(ctypes.c_uint64),
    ctypes.c_uint32,
]
_lib.yoimiya_prove_test_precompiled.restype = ctypes.POINTER(YoimiyaProof)

_lib.yoimiya_prove_r1cs.argtypes = [
    ctypes.c_char_p,
    ctypes.POINTER(ctypes.c_uint64),
    ctypes.c_uint32,
    ctypes.POINTER(YoimiyaSrs)
]
_lib.yoimiya_prove_r1cs.restype = ctypes.POINTER(YoimiyaProof)

_lib.yoimiya_prove_r1cs_field.argtypes = [
    ctypes.c_char_p,
    ctypes.POINTER(ctypes.c_uint8),
    ctypes.c_uint32,
    ctypes.POINTER(YoimiyaSrs)
]
_lib.yoimiya_prove_r1cs_field.restype = ctypes.POINTER(YoimiyaProof)

_lib.yoimiya_prove_acir.argtypes = [
    ctypes.c_char_p,
    ctypes.POINTER(ctypes.c_uint64),
    ctypes.c_uint32,
    ctypes.POINTER(YoimiyaSrs)
]
_lib.yoimiya_prove_acir.restype = ctypes.POINTER(YoimiyaProof)

_lib.yoimiya_prove_plonkish.argtypes = [
    ctypes.c_char_p,
    ctypes.POINTER(ctypes.c_uint64),
    ctypes.c_uint32,
    ctypes.POINTER(YoimiyaSrs)
]
_lib.yoimiya_prove_plonkish.restype = ctypes.POINTER(YoimiyaProof)

_lib.yoimiya_free_proof.argtypes = [ctypes.POINTER(YoimiyaProof)]
_lib.yoimiya_free_proof.restype = None

_lib.yoimiya_proof_size_bytes.argtypes = [ctypes.POINTER(YoimiyaProof)]
_lib.yoimiya_proof_size_bytes.restype = ctypes.c_int32

# Verification
_lib.yoimiya_verify.argtypes = [ctypes.POINTER(YoimiyaProof), ctypes.POINTER(YoimiyaSrs)]
_lib.yoimiya_verify.restype = ctypes.c_int32

_lib.yoimiya_verify_precompiled.argtypes = [ctypes.POINTER(YoimiyaProof)]
_lib.yoimiya_verify_precompiled.restype = ctypes.c_int32

# Aggregation
_lib.yoimiya_aggregate.argtypes = [
    ctypes.POINTER(ctypes.POINTER(YoimiyaProof)),
    ctypes.c_uint32,
    ctypes.POINTER(YoimiyaSrs)
]
_lib.yoimiya_aggregate.restype = ctypes.POINTER(YoimiyaBatchProof)

_lib.yoimiya_free_batch_proof.argtypes = [ctypes.POINTER(YoimiyaBatchProof)]
_lib.yoimiya_free_batch_proof.restype = None

# Serialize batch proof to 275-byte EVM calldata; returns bytes written or -1 on error
_lib.yoimiya_batch_to_calldata.argtypes = [
    ctypes.POINTER(YoimiyaBatchProof),
    ctypes.POINTER(ctypes.c_uint8),
    ctypes.c_uint32
]
_lib.yoimiya_batch_to_calldata.restype = ctypes.c_int32

# Hardware detection — returns a by-value struct (no pointer, no free needed)
class _YoimiyaHwInfo(ctypes.Structure):
    _fields_ = [
        ("logical_cores",          ctypes.c_uint32),
        ("tier",                   ctypes.c_uint32),  # 0=Mobile 1=Desktop 2=Server 3=HPC
        ("partitions",             ctypes.c_uint32),
        ("segments_per_partition", ctypes.c_uint32),
        ("total_threads",          ctypes.c_uint32),
    ]

_lib.yoimiya_detect_hardware.argtypes = []
_lib.yoimiya_detect_hardware.restype = _YoimiyaHwInfo

_lib.yoimiya_optimal_partitions.argtypes = [ctypes.c_uint32]
_lib.yoimiya_optimal_partitions.restype = ctypes.c_uint32

_lib.yoimiya_precompiled_srs_degree.argtypes = [ctypes.c_uint32]
_lib.yoimiya_precompiled_srs_degree.restype = ctypes.c_uint32

_TIER_LABELS = {0: "Mobile", 1: "Desktop", 2: "Server", 3: "HPC"}

def hardware_info() -> dict:
    """
    Detect host hardware and return optimal proving parameters.

    Returns a dict with:
      logical_cores          - number of logical CPU cores
      tier                   - "Mobile" / "Desktop" / "Server" / "HPC"
      partitions             - base partition count for this hardware tier
      segments_per_partition - intra-partition segments
      total_threads          - effective parallelism (partitions × segments)
    """
    hw = _lib.yoimiya_detect_hardware()
    return {
        "logical_cores":          hw.logical_cores,
        "tier":                   _TIER_LABELS.get(hw.tier, "Unknown"),
        "partitions":             hw.partitions,
        "segments_per_partition": hw.segments_per_partition,
        "total_threads":          hw.total_threads,
    }


def optimal_partitions(num_constraints: int) -> int:
    """
    Return the partition count that prove() will actually use for a circuit
    of this size on the current machine.

    Combines hardware tier ceiling with circuit size floor:
      - < 8K constraints  → 2  (folding overhead dominates at small scale)
      - 8K  – 16K         → 2
      - 16K – 64K         → 4–8
      - 64K – 512K        → 8–16
      - 512K+             → up to logical_cores (power-of-two, max 64)
    """
    return int(_lib.yoimiya_optimal_partitions(num_constraints))


def precompiled_srs_degree(num_constraints: int) -> int:
    """Return bundled precompiled SRS degree used for this constraint count."""
    return int(_lib.yoimiya_precompiled_srs_degree(num_constraints))

# ──────────────────────────────────────────────────────────────────
# Python Wrapper Classes
# ──────────────────────────────────────────────────────────────────

class Srs:
    """Structured Reference String (SRS) for proving and verification."""
    
    def __init__(self, max_degree: int):
        """
        Generate a test SRS.
        
        Args:
            max_degree: Maximum polynomial degree the SRS supports.
        """
        self._srs = _lib.yoimiya_generate_test_srs(max_degree)
        if not self._srs:
            raise RuntimeError("Failed to generate SRS")
        self.max_degree = max_degree
    
    def __del__(self):
        """Free the SRS when garbage collected."""
        if hasattr(self, '_srs') and self._srs:
            _lib.yoimiya_free_srs(self._srs)
    
    @property
    def handle(self) -> ctypes.POINTER(YoimiyaSrs):
        """Get the underlying C handle."""
        return self._srs


class Proof:
    """Zero-knowledge proof."""
    
    def __init__(self, handle: ctypes.POINTER(YoimiyaProof)):
        """Initialize with a proof handle."""
        self._proof = handle
    
    def __del__(self):
        """Free the proof when garbage collected."""
        if hasattr(self, '_proof') and self._proof:
            _lib.yoimiya_free_proof(self._proof)
    
    def verify(self, srs: Srs) -> bool:
        """
        Verify this proof.
        
        Args:
            srs: The SRS used for proving.
        
        Returns:
            True if valid, False otherwise.
        """
        result = _lib.yoimiya_verify(self._proof, srs.handle)
        if result == -1:
            raise RuntimeError("Verification error")
        return result == 1

    def verify_precompiled(self) -> bool:
        """Verify this proof with bundled precompiled SRS."""
        result = _lib.yoimiya_verify_precompiled(self._proof)
        if result == -1:
            raise RuntimeError("Verification error")
        return result == 1

    def byte_size(self) -> int:
        """Return compressed serialized proof size in bytes."""
        size = _lib.yoimiya_proof_size_bytes(self._proof)
        if size < 0:
            raise RuntimeError("Failed to get proof byte size")
        return int(size)
    
    @property
    def handle(self) -> ctypes.POINTER(YoimiyaProof):
        """Get the underlying C handle."""
        return self._proof


class BatchProof:
    """Aggregated batch proof."""
    
    def __init__(self, handle: ctypes.POINTER(YoimiyaBatchProof)):
        """Initialize with a batch proof handle."""
        self._batch_proof = handle
    
    def __del__(self):
        """Free the batch proof when garbage collected."""
        if hasattr(self, '_batch_proof') and self._batch_proof:
            _lib.yoimiya_free_batch_proof(self._batch_proof)
    
    def to_calldata(self) -> bytes:
        """
        Serialize this batch proof to EVM calldata (275 bytes).
        
        Returns:
            bytes: 275-byte calldata for the on-chain verifier.
        """
        buf = (ctypes.c_uint8 * 275)()
        written = _lib.yoimiya_batch_to_calldata(self._batch_proof, buf, 275)
        if written < 0:
            raise RuntimeError("Failed to serialize batch proof")
        return bytes(buf[:written])

    def verify(self, srs: Srs) -> bool:
        """
        Verify this batch proof by confirming it serializes to valid calldata.
        
        Note: Full cryptographic batch verification is performed on-chain via
        YoimiyaBatchVerifier.sol. This check confirms the proof is well-formed.
        
        Returns:
            True if the proof serializes successfully, False otherwise.
        """
        try:
            data = self.to_calldata()
            return len(data) == 275
        except RuntimeError:
            return False


# ──────────────────────────────────────────────────────────────────
# Public API
# ──────────────────────────────────────────────────────────────────

def generate_test_srs(max_degree: int) -> Srs:
    """
    Generate a deterministic test SRS.
    
    Args:
        max_degree: Maximum polynomial degree.
    
    Returns:
        Srs object.
    """
    return Srs(max_degree)


def prove_test(
    num_constraints: int,
    witness: List[int] = None,
    srs: Srs = None,
) -> Proof:
    """
    Prove a test circuit.
    
    Args:
        num_constraints: Number of R1CS constraints.
        witness: Optional list of witness values (u64).
                 Auto-padded with 1s to num_constraints+1 if too short.
                 Defaults to [1]*(num_constraints+1) if omitted.
        srs: Structured Reference String.
    
    Returns:
        Proof object.
    """
    if srs is None:
        raise ValueError("srs is required")
    required = num_constraints + 1
    if witness is None:
        witness = [1] * required
    elif len(witness) < required:
        witness = list(witness) + [1] * (required - len(witness))

    witness_array = (ctypes.c_uint64 * len(witness))(*witness)
    proof_handle = _lib.yoimiya_prove_test(
        num_constraints,
        witness_array,
        len(witness),
        srs.handle
    )
    if not proof_handle:
        raise RuntimeError("Failed to prove")
    return Proof(proof_handle)


def prove_test_precompiled(
    num_constraints: int,
    witness: List[int] = None,
) -> Proof:
    """
    Prove a test circuit using bundled precompiled SRS.

    No explicit SRS handle is required.
    Witness auto-padded with 1s if too short or omitted.
    """
    required = num_constraints + 1
    if witness is None:
        witness = [1] * required
    elif len(witness) < required:
        witness = list(witness) + [1] * (required - len(witness))

    witness_array = (ctypes.c_uint64 * len(witness))(*witness)
    proof_handle = _lib.yoimiya_prove_test_precompiled(
        num_constraints,
        witness_array,
        len(witness),
    )
    if not proof_handle:
        raise RuntimeError("Failed to prove")
    return Proof(proof_handle)


def prove_r1cs(
    r1cs_path: str,
    witness: List[int],
    srs: Srs
) -> Proof:
    """
    Prove an R1CS circuit.
    
    Args:
        r1cs_path: Path to the .r1cs file.
        witness: List of witness values (u64).
        srs: Structured Reference String.
    
    Returns:
        Proof object.
    """
    witness_array = (ctypes.c_uint64 * len(witness))(*witness)
    proof_handle = _lib.yoimiya_prove_r1cs(
        r1cs_path.encode('utf-8'),
        witness_array,
        len(witness),
        srs.handle
    )
    if not proof_handle:
        raise RuntimeError("Failed to prove R1CS")
    return Proof(proof_handle)


def prove_r1cs_field(
    r1cs_path: str,
    witness: List[int],
    srs: Srs
) -> Proof:
    """
    Prove an R1CS circuit with full BN254 field-element witnesses.

    Unlike prove_r1cs(), this function correctly handles witness values that
    exceed 2^64, as produced by Circom/snarkjs for circuits with non-trivial
    intermediate signals (MiMC, Poseidon, etc.).

    Each integer in `witness` is encoded as a 32-byte little-endian BN254
    scalar field element before being passed to the native library.

    Args:
        r1cs_path: Path to the .r1cs file compiled by circom.
        witness: List of Python ints (arbitrary size, reduced mod BN254 prime).
        srs: Structured Reference String.

    Returns:
        Proof object.
    """
    # BN254 scalar field prime (Fr), per EIP-197 / arkworks bn254 crate
    _BN254_R = 0x30644e72e131a029b85045b68181585d2833e84879b9709142e1f0121e840101

    # Encode each field element as 32-byte LE, reduced mod p
    buf = bytearray()
    for v in witness:
        fe = int(v) % _BN254_R
        buf.extend(fe.to_bytes(32, 'little'))

    byte_array = (ctypes.c_uint8 * len(buf))(*buf)
    proof_handle = _lib.yoimiya_prove_r1cs_field(
        r1cs_path.encode('utf-8'),
        byte_array,
        len(witness),
        srs.handle
    )
    if not proof_handle:
        raise RuntimeError("Failed to prove R1CS with field witnesses")
    return Proof(proof_handle)


def prove_acir(
    acir_path: str,
    witness: List[int],
    srs: Srs
) -> Proof:
    """
    Prove an ACIR circuit.

    Args:
        acir_path: Path to the .acir file.
        witness: List of witness values (u64).
        srs: Structured Reference String.

    Returns:
        Proof object.
    """
    witness_array = (ctypes.c_uint64 * len(witness))(*witness)
    proof_handle = _lib.yoimiya_prove_acir(
        acir_path.encode('utf-8'),
        witness_array,
        len(witness),
        srs.handle
    )
    if not proof_handle:
        raise RuntimeError("Failed to prove ACIR")
    return Proof(proof_handle)


def prove_plonkish(
    plonkish_path: str,
    witness: List[int],
    srs: Srs
) -> Proof:
    """
    Prove a Plonkish circuit.

    Args:
        plonkish_path: Path to the .plonkish file.
        witness: List of witness values (u64).
        srs: Structured Reference String.

    Returns:
        Proof object.
    """
    witness_array = (ctypes.c_uint64 * len(witness))(*witness)
    proof_handle = _lib.yoimiya_prove_plonkish(
        plonkish_path.encode('utf-8'),
        witness_array,
        len(witness),
        srs.handle
    )
    if not proof_handle:
        raise RuntimeError("Failed to prove Plonkish")
    return Proof(proof_handle)


def aggregate_proofs(proofs: List[Proof], srs: Srs) -> BatchProof:
    """
    Aggregate multiple proofs into a single batch proof.
    
    Args:
        proofs: List of Proof objects.
        srs: Structured Reference String.
    
    Returns:
        BatchProof object.
    """
    if not proofs:
        raise ValueError("No proofs to aggregate")
    
    proof_handles = (ctypes.POINTER(YoimiyaProof) * len(proofs))(
        *[p.handle for p in proofs]
    )
    batch_handle = _lib.yoimiya_aggregate(
        proof_handles,
        len(proofs),
        srs.handle
    )
    if not batch_handle:
        raise RuntimeError("Failed to aggregate proofs")
    return BatchProof(batch_handle)


__all__ = [
    'Srs',
    'Proof',
    'BatchProof',
    'hardware_info',
    'optimal_partitions',
    'precompiled_srs_degree',
    'generate_test_srs',
    'prove_test',
    'prove_test_precompiled',
    'prove_r1cs',
    'prove_acir',
    'prove_plonkish',
    'aggregate_proofs',
]
