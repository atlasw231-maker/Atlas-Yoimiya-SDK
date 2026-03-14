#!/usr/bin/env python3
"""
Real Circom circuit proving test for Yoimiya SDK.

This script tests Yoimiya against circuits compiled from real Circom source using
circom2 + snarkjs. Unlike synthetic circuit generators, these are:
  - Compiled from Circom source via `npx circom2 --r1cs --wasm`
  - Witnesses computed by the Circom WASM witness generator via `npx snarkjs wc`
  - Witnesses contain real BN254 field elements (not degenerate all-1s values)

Circuits tested:
  1. range_proof.circom  — 32-bit range check, 64 constraints (all u64-safe witness)
  2. mimc_hash.circom    — MiMC-7 hash, 364 constraints (full field element witness)
  3. poseidon_perm.circom— Poseidon permutation, 900 constraints (full field element witness)

Usage:
    cd "C:\\Users\\Miko De La Paz\\yoimiya-sdk-0.1.0"
    python circom_circuit_test.py
"""
import sys
import os
import json
import time
import subprocess

# ── paths ────────────────────────────────────────────────────────────────────
SDK_DIR   = os.path.dirname(os.path.abspath(__file__))
CIRC_DIR  = os.path.join(SDK_DIR, "circuits")
BUILD_DIR = os.path.join(CIRC_DIR, "build")

sys.path.insert(0, os.path.join(SDK_DIR, "bindings", "python"))
import yoimiya as y

# ── helpers ──────────────────────────────────────────────────────────────────
def green(s):  return f"\033[92m{s}\033[0m"
def red(s):    return f"\033[91m{s}\033[0m"
def bold(s):   return f"\033[1m{s}\033[0m"


def load_witness_json(path: str) -> list[int]:
    """Load a snarkjs witness.json (array of decimal strings) -> list of ints."""
    with open(path) as f:
        raw = json.load(f)
    return [int(v) for v in raw]


def witness_max_bits(witness: list[int]) -> int:
    """Return the bit-width of the largest value in the witness."""
    mx = max(witness)
    return mx.bit_length()


def ensure_witness(circuit_name: str, wasm_path: str, input_json: str, wtns_path: str, witness_json_path: str):
    """(Re-)generate witness if the JSON doesn't exist yet."""
    if os.path.exists(witness_json_path):
        return
    print(f"  Generating witness for {circuit_name}...")
    subprocess.run(
        ["npx", "snarkjs", "wc", wasm_path, input_json, wtns_path],
        check=True, capture_output=True
    )
    subprocess.run(
        ["npx", "snarkjs", "wej", wtns_path, witness_json_path],
        check=True, capture_output=True
    )


def prove_and_verify(label: str, r1cs_path: str, witness: list[int], num_constraints: int, use_field_api: bool):
    """Prove and verify a circuit, print timing and result."""
    # Add 10% headroom so a slightly wrong constraint count doesn't fail
    srs = y.generate_test_srs(int(num_constraints * 1.1) + 16)

    t0 = time.perf_counter()
    if use_field_api:
        proof = y.prove_r1cs_field(r1cs_path, witness, srs)
    else:
        proof = y.prove_r1cs(r1cs_path, witness, srs)
    prove_ms = (time.perf_counter() - t0) * 1000

    t1 = time.perf_counter()
    ok = proof.verify(srs)
    verify_ms = (time.perf_counter() - t1) * 1000

    status = green("PASS") if ok else red("FAIL")
    api_tag = "field-API" if use_field_api else "u64-API "
    print(f"  [{status}] {label:35s}  prove={prove_ms:7.1f}ms  verify={verify_ms:6.1f}ms  ({api_tag})")
    return ok


# ── main ─────────────────────────────────────────────────────────────────────
def main():
    print(bold("\n=== Yoimiya Real Circom Circuit Test ===\n"))

    # ── 1. range_proof ────────────────────────────────────────────────────────
    print(bold("Circuit 1: range_proof.circom (32-bit range check)"))
    print("  Source:      circuits/range_proof.circom")
    print("  Constraints: 64  (32 bits × 2 decompositions + 2 reconstruction checks)")
    print("  Input:       value=12345678  max_value=2147483647 (2^31-1)")
    print("  Witness API: u64 (all values ≤ 2^31, fits in u64)")

    r1cs_range   = os.path.join(BUILD_DIR, "range", "range_proof.r1cs")
    wasm_range   = os.path.join(BUILD_DIR, "range", "range_proof_js", "range_proof.wasm")
    input_range  = os.path.join(CIRC_DIR, "range_input.json")
    wtns_range   = os.path.join(BUILD_DIR, "range", "witness.wtns")
    wjson_range  = os.path.join(BUILD_DIR, "range", "witness.json")
    ensure_witness("range_proof", wasm_range, input_range, wtns_range, wjson_range)

    witness_range = load_witness_json(wjson_range)
    print(f"  Signals:     {len(witness_range)}  (max value: {max(witness_range)}, bit-width: {witness_max_bits(witness_range)})")

    ok1 = prove_and_verify(
        "range_proof [value=12345678, max=2^31-1]",
        r1cs_range, witness_range, 64, use_field_api=False
    )

    # ── 2. mimc_hash ──────────────────────────────────────────────────────────
    print()
    print(bold("Circuit 2: mimc_hash.circom (MiMC-7, 91 rounds)"))
    print("  Source:      circuits/mimc_hash.circom")
    print("  Constraints: 366  (91 rounds × 4 mult constraints + 2 linear)")
    print("  Input:       x_in=7  k=13")
    print("  Witness API: field (intermediate states are BN254 field elements)")

    r1cs_mimc   = os.path.join(BUILD_DIR, "mimc", "mimc_hash.r1cs")
    wasm_mimc   = os.path.join(BUILD_DIR, "mimc", "mimc_hash_js", "mimc_hash.wasm")
    input_mimc  = os.path.join(CIRC_DIR, "mimc_input.json")
    wtns_mimc   = os.path.join(BUILD_DIR, "mimc", "witness.wtns")
    wjson_mimc  = os.path.join(BUILD_DIR, "mimc", "witness.json")
    ensure_witness("mimc_hash", wasm_mimc, input_mimc, wtns_mimc, wjson_mimc)

    witness_mimc = load_witness_json(wjson_mimc)
    large_count  = sum(1 for v in witness_mimc if v >= 2**64)
    print(f"  Signals:     {len(witness_mimc)}  ({large_count} exceed u64 — need field API)")

    ok2 = prove_and_verify(
        "mimc_hash  [x_in=7, k=13]",
        r1cs_mimc, witness_mimc, 366, use_field_api=True
    )

    # ── 3. poseidon_perm ──────────────────────────────────────────────────────
    print()
    print(bold("Circuit 3: poseidon_perm.circom (Poseidon-style, 100 rounds)"))
    print("  Source:      circuits/poseidon_perm.circom")
    print("  Constraints: 1500  (900 non-linear + 600 linear: 100 rounds × 3 lanes × Pow5)")
    print("  Input:       state=[1, 2, 3]")
    print("  Witness API: field (all intermediate states are BN254 field elements)")

    r1cs_pos    = os.path.join(BUILD_DIR, "poseidon", "poseidon_perm.r1cs")
    wasm_pos    = os.path.join(BUILD_DIR, "poseidon", "poseidon_perm_js", "poseidon_perm.wasm")
    input_pos   = os.path.join(CIRC_DIR, "poseidon_input.json")
    wtns_pos    = os.path.join(BUILD_DIR, "poseidon", "witness.wtns")
    wjson_pos   = os.path.join(BUILD_DIR, "poseidon", "witness.json")
    ensure_witness("poseidon_perm", wasm_pos, input_pos, wtns_pos, wjson_pos)

    witness_pos   = load_witness_json(wjson_pos)
    large_count_p = sum(1 for v in witness_pos if v >= 2**64)
    print(f"  Signals:     {len(witness_pos)}  ({large_count_p} exceed u64 — need field API)")

    ok3 = prove_and_verify(
        "poseidon_perm [state=[1,2,3]]",
        r1cs_pos, witness_pos, 1500, use_field_api=True
    )

    # ── 4. Cross-check: range_proof also works via the field API ───────────────
    print()
    print(bold("Cross-check: range_proof via field API (should match u64 API result)"))
    ok4 = prove_and_verify(
        "range_proof [field-API cross-check]",
        r1cs_range, witness_range, 64, use_field_api=True
    )

    # ── Summary ───────────────────────────────────────────────────────────────
    print()
    print(bold("=== Summary ==="))
    tests = [
        ("range_proof  (u64-API)", ok1),
        ("mimc_hash    (field-API)", ok2),
        ("poseidon_perm(field-API)", ok3),
        ("range_proof  (field-API cross-check)", ok4),
    ]
    all_pass = True
    for name, ok in tests:
        status = green("PASS") if ok else red("FAIL")
        print(f"  [{status}] {name}")
        all_pass = all_pass and ok

    print()
    if all_pass:
        print(green("All tests PASSED — real Circom circuits proved and verified successfully."))
    else:
        print(red("Some tests FAILED."))
        sys.exit(1)


if __name__ == "__main__":
    main()
