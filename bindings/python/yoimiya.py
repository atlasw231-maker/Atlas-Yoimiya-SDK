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
    search_paths = [
        lib_name,
        f"./lib/{lib_name}",
        f"./sdk/platforms/{system.lower()}-{machine}/{lib_name}",
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

_lib.yoimiya_prove_r1cs.argtypes = [
    ctypes.c_char_p,
    ctypes.POINTER(ctypes.c_uint64),
    ctypes.c_uint32,
    ctypes.POINTER(YoimiyaSrs)
]
_lib.yoimiya_prove_r1cs.restype = ctypes.POINTER(YoimiyaProof)

_lib.yoimiya_free_proof.argtypes = [ctypes.POINTER(YoimiyaProof)]
_lib.yoimiya_free_proof.restype = None

# Verification
_lib.yoimiya_verify.argtypes = [ctypes.POINTER(YoimiyaProof), ctypes.POINTER(YoimiyaSrs)]
_lib.yoimiya_verify.restype = ctypes.c_int32

# Aggregation
_lib.yoimiya_aggregate.argtypes = [
    ctypes.POINTER(ctypes.POINTER(YoimiyaProof)),
    ctypes.c_uint32,
    ctypes.POINTER(YoimiyaSrs)
]
_lib.yoimiya_aggregate.restype = ctypes.POINTER(YoimiyaBatchProof)

_lib.yoimiya_free_batch_proof.argtypes = [ctypes.POINTER(YoimiyaBatchProof)]
_lib.yoimiya_free_batch_proof.restype = None

_lib.yoimiya_verify_batch.argtypes = [
    ctypes.POINTER(YoimiyaBatchProof),
    ctypes.POINTER(YoimiyaSrs)
]
_lib.yoimiya_verify_batch.restype = ctypes.c_int32

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
    
    def verify(self, srs: Srs) -> bool:
        """
        Verify this batch proof.
        
        Args:
            srs: The SRS used for proving.
        
        Returns:
            True if valid, False otherwise.
        """
        result = _lib.yoimiya_verify_batch(self._batch_proof, srs.handle)
        if result == -1:
            raise RuntimeError("Batch verification error")
        return result == 1


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
    witness: List[int],
    srs: Srs
) -> Proof:
    """
    Prove a test circuit.
    
    Args:
        num_constraints: Number of R1CS constraints.
        witness: List of witness values (u64).
        srs: Structured Reference String.
    
    Returns:
        Proof object.
    """
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
    'generate_test_srs',
    'prove_test',
    'prove_r1cs',
    'aggregate_proofs',
]
