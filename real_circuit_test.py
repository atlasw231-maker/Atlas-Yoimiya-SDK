"""
Yoimiya Real Circuit Test

Tests the SDK against programmatically generated real circuit files via the
file-based API (prove_r1cs / prove_acir), covering three distinct arithmetic
patterns:

  1. Fibonacci  (addition chain — linear R1CS)
  2. Mul-chain  (multiplicative Fibonacci — Mul-only R1CS)
  3. Range-check (bit decomposition — quadratic R1CS: b*(b-1)=0)
  4. MiMC-round (cube chain via ACIR Mul opcodes)

For constraint sizes > 50k the script falls back to the precompiled SRS
test circuit (prove_test_precompiled), clearly labelling the code path.

Usage:
    python real_circuit_test.py                     # defaults
    python real_circuit_test.py --sizes 100 1000    # only these sizes
    python real_circuit_test.py --iterations 5      # 5 reps per circuit
    python real_circuit_test.py --max-file-size 10000  # cap file circuits
"""

import argparse
import ctypes
import math
import platform
import struct
import sys
import tempfile
import threading
import time
from pathlib import Path

BINDINGS = Path(__file__).parent / "bindings" / "python"
sys.path.insert(0, str(BINDINGS))

import yoimiya as y

# ─── BN254 scalar field prime ────────────────────────────────────────────────
BN254_R = 21888242871839275222246405745257275088548364400416034343698204186575808495617


# ─── helpers ─────────────────────────────────────────────────────────────────

def _encode_fr(value: int) -> bytes:
    """Python int → 32-byte little-endian BN254 field element."""
    return (value % BN254_R).to_bytes(32, "little")


def _write_constraint(a_terms, b_terms, c_terms) -> bytes:
    """Serialize one R1CS constraint (3 sparse rows) in raw format."""
    data = b""
    for terms in (a_terms, b_terms, c_terms):
        data += struct.pack("<I", len(terms))
        for var_idx, coeff in terms:
            data += struct.pack("<I", var_idx)
            data += _encode_fr(coeff)
    return data


def _write_r1cs_raw(constraints, num_vars, num_public) -> bytes:
    """
    Build a raw R1CS file (no 'r1cs' magic — triggers parse_r1cs_raw in the SDK).

    constraints: list of (a_terms, b_terms, c_terms)
    """
    header = struct.pack("<III", len(constraints), num_vars, num_public)
    body = b"".join(_write_constraint(a, b, c) for a, b, c in constraints)
    return header + body


def _write_acir(opcodes, num_witnesses, num_public) -> bytes:
    """
    Build an ACIR file (opcode-based).

    Supported opcodes:
      (0, [(var, coeff), ...])  — AssertZero linear combination = 0
      (1, va, vb, vc)           — Mul: va * vb = vc
    """
    header = struct.pack("<II", num_witnesses, num_public)
    body = b""
    for op in opcodes:
        if op[0] == 0:  # AssertZero
            terms = op[1]
            body += struct.pack("<I", 0)
            body += struct.pack("<I", len(terms))
            for var_idx, coeff in terms:
                body += struct.pack("<I", var_idx)
                body += _encode_fr(coeff)
        elif op[0] == 1:  # Mul
            _, va, vb, vc = op
            body += struct.pack("<I", 1)
            body += struct.pack("<III", va, vb, vc)
    return header + body


# ─── circuit generators ───────────────────────────────────────────────────────

def make_fibonacci_r1cs(n: int):
    """
    Fibonacci addition circuit: F[i] + F[i+1] = F[i+2], n constraints.

    Variable layout:
      var[0]           = constant-1 wire (witness[0] = 1)
      var[1..n+2]      = F[0]..F[n+1]
    Total variables:  n+3
    """
    constraints = []
    for i in range(n):
        a = [(1 + i, 1), (2 + i, 1)]   # F[i] + F[i+1]
        b = [(0, 1)]                     # × 1 (constant wire)
        c = [(3 + i, 1)]                 # = F[i+2]
        constraints.append((a, b, c))

    # Compute witness: [1, F(0), F(1), ..., F(n+1)]
    fibs = [1, 1]
    for _ in range(n):
        fibs.append((fibs[-1] + fibs[-2]) % BN254_R)
    witness = [1] + fibs  # var[0]=1, then F[0]..F[n+1]

    data = _write_r1cs_raw(constraints, n + 3, 1)
    return data, witness


def make_mulchain_r1cs(n: int):
    """
    Multiplicative Fibonacci: x[i] * x[i+1] = x[i+2], n constraints.

    Each element is the product of the two predecessors — different structure
    from the trivial squaring chain in test_circuit (which does x[i]*x[i]=x[i+1]).

    Variable layout: var[0..n+1], total n+2 variables.
    Witness: [2, 3, 6, 18, 108, ...] (mul-chain mod BN254_R)
    """
    constraints = []
    for i in range(n):
        a = [(i, 1)]
        b = [(i + 1, 1)]
        c = [(i + 2, 1)]
        constraints.append((a, b, c))

    w = [2, 3]
    for i in range(n):
        w.append((w[i] * w[i + 1]) % BN254_R)
    witness = w  # n+2 values

    data = _write_r1cs_raw(constraints, n + 2, 1)
    return data, witness


def make_rangecheck_r1cs(n: int):
    """
    Bit decomposition / range check: b[i] * (b[i] - 1) = 0, n constraints.

    Each constraint verifies one bit is in {0, 1}.

    Variable layout:
      var[0]       = constant-1 wire (witness[0] = 1)
      var[1..n]    = bits b[0..n-1]
    Total: n+1 variables.
    Witness: [1, alternating 0/1 bits]
    """
    constraints = []
    for i in range(n):
        # b[i] * (b[i] - 1) = 0
        # A = [(i+1, 1)]
        # B = [(i+1, 1), (0, -1)]   →  B·w = b[i] - 1
        # C = []
        a = [(i + 1, 1)]
        b = [(i + 1, 1), (0, BN254_R - 1)]  # -1 mod p
        c = []
        constraints.append((a, b, c))

    bits = [i % 2 for i in range(n)]
    witness = [1] + bits  # var[0]=1, then bits

    data = _write_r1cs_raw(constraints, n + 1, 1)
    return data, witness


def make_mimc_acir(n: int):
    """
    MiMC-style cube chain via ACIR Mul opcodes: x[i]^3 = x[i+2].

    Each round uses 2 Mul opcodes:
      t = x[i] * x[i]      (square: Mul  i, i, temp)
      y = t   * x[i]       (cube:   Mul  temp, i, i+1)

    Since n must be even for this layout, we pad by 1 if odd.
    Effective constraints = 2 * ceil(n / 2).

    Variable layout: [x[0], t[0], x[1], t[1], ..., x[m]] where m = ceil(n/2)
    x variables at even indices: 0, 2, 4, ...
    temp variables at odd indices: 1, 3, 5, ...
    """
    rounds = (n + 1) // 2  # ceil
    num_constraints = rounds * 2
    # Variables: rounds pairs (x, t) + final x = 2*rounds + 1
    total_vars = 2 * rounds + 1

    opcodes = []
    for r in range(rounds):
        x_i = 2 * r        # current x
        t_i = 2 * r + 1    # temp = x^2
        x_next = 2 * r + 2 # next x = x^3
        opcodes.append((1, x_i, x_i, t_i))       # t = x * x
        opcodes.append((1, t_i, x_i, x_next))    # next_x = t * x

    # Compute witness: x[r+1] = x[r]^3 mod p
    xs = [2]  # x[0] = 2
    ts = []
    for r in range(rounds):
        t = (xs[r] * xs[r]) % BN254_R
        xn = (t * xs[r]) % BN254_R
        ts.append(t)
        xs.append(xn)

    # Interleave into witness array at the correct variable positions
    witness = [0] * total_vars
    for r in range(rounds):
        witness[2 * r] = xs[r]
        witness[2 * r + 1] = ts[r]
    witness[2 * rounds] = xs[rounds]

    # The SDK sets num_variables = num_witnesses + 1 (constant wire slot),
    # so the witness array must have total_vars + 1 entries.
    witness.append(0)

    data = _write_acir(opcodes, total_vars, 1)
    return data, witness, num_constraints


# ─── memory sampling ──────────────────────────────────────────────────────────

def _current_rss_bytes():
    if platform.system() == "Windows":
        import ctypes as ct
        from ctypes import wintypes

        class _PMC(ct.Structure):
            _fields_ = [
                ("cb", wintypes.DWORD),
                ("PageFaultCount", wintypes.DWORD),
                ("PeakWorkingSetSize", ct.c_size_t),
                ("WorkingSetSize", ct.c_size_t),
                ("QuotaPeakPagedPoolUsage", ct.c_size_t),
                ("QuotaPagedPoolUsage", ct.c_size_t),
                ("QuotaPeakNonPagedPoolUsage", ct.c_size_t),
                ("QuotaNonPagedPoolUsage", ct.c_size_t),
                ("PagefileUsage", ct.c_size_t),
                ("PeakPagefileUsage", ct.c_size_t),
            ]

        pmc = _PMC()
        pmc.cb = ct.sizeof(_PMC)
        k32 = ct.WinDLL("kernel32", use_last_error=True)
        psapi = ct.WinDLL("psapi", use_last_error=True)
        k32.GetCurrentProcess.restype = wintypes.HANDLE
        psapi.GetProcessMemoryInfo.argtypes = [
            wintypes.HANDLE, ct.POINTER(_PMC), wintypes.DWORD,
        ]
        psapi.GetProcessMemoryInfo.restype = wintypes.BOOL
        if psapi.GetProcessMemoryInfo(
            k32.GetCurrentProcess(), ct.byref(pmc), pmc.cb
        ):
            return int(pmc.WorkingSetSize)
    stat = Path("/proc/self/status")
    if stat.exists():
        for line in stat.read_text().splitlines():
            if line.startswith("VmRSS:"):
                parts = line.split()
                return int(parts[1]) * 1024 if len(parts) >= 2 else None
    return None


class _PeakSampler:
    def __init__(self, interval=0.01):
        self._stop = threading.Event()
        self._thread = None
        self.peak = _current_rss_bytes() or 0

    def start(self):
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()

    def stop(self):
        self._stop.set()
        if self._thread:
            self._thread.join()
        cur = _current_rss_bytes()
        if cur:
            self.peak = max(self.peak, cur)
        return self.peak

    def _run(self):
        while not self._stop.wait(0.01):
            cur = _current_rss_bytes()
            if cur:
                self.peak = max(self.peak, cur)


def _mb(b):
    return b / (1024 ** 2) if b else 0.0


# ─── statistics ───────────────────────────────────────────────────────────────

def _stats(values):
    if not values:
        return {}
    n = len(values)
    avg = sum(values) / n
    return {
        "avg": avg,
        "min": min(values),
        "max": max(values),
        "stddev": math.sqrt(sum((v - avg) ** 2 for v in values) / n),
    }


def _fmt_stat(s):
    return (
        f"avg={s['avg']:.3f}ms  "
        f"min={s['min']:.3f}ms  "
        f"max={s['max']:.3f}ms  "
        f"σ={s['stddev']:.3f}ms"
    )


# ─── test runner ─────────────────────────────────────────────────────────────

CIRCUIT_DEFS = {
    "fibonacci":   ("R1CS", make_fibonacci_r1cs,  False),
    "mul-chain":   ("R1CS", make_mulchain_r1cs,   False),
    "range-check": ("R1CS", make_rangecheck_r1cs, False),
    "mimc-acir":   ("ACIR", make_mimc_acir,       True),   # extra return: actual_constraints
}


def run_file_circuit(name, size, iterations, tmpdir) -> dict:
    """
    Build a circuit file, prove & verify `iterations` times, return stats.
    """
    label, builder, has_actual_constraints = CIRCUIT_DEFS[name]

    # Build circuit file
    t_build = time.perf_counter()
    if has_actual_constraints:
        data, witness, actual_n = builder(size)
    else:
        data, witness = builder(size)
        actual_n = size
    build_ms = (time.perf_counter() - t_build) * 1000

    # Write to temp file
    suffix = ".acir" if label == "ACIR" else ".r1cs"
    fpath = tmpdir / f"{name}_{actual_n}{suffix}"
    fpath.write_bytes(data)

    # SRS: sized to fit just above constraint count (reuse across iterations)
    srs_degree = actual_n + 1
    srs = y.generate_test_srs(srs_degree)

    prove_times = []
    verify_times = []
    peak_mb_max = 0.0
    all_valid = True

    for i in range(1, iterations + 1):
        sampler = _PeakSampler()
        sampler.start()
        try:
            t0 = time.perf_counter()
            if label == "R1CS":
                proof = y.prove_r1cs(str(fpath), witness, srs)
            else:
                proof = y.prove_acir(str(fpath), witness, srs)
            prove_ms = (time.perf_counter() - t0) * 1000

            t0 = time.perf_counter()
            valid = proof.verify(srs)
            verify_ms = (time.perf_counter() - t0) * 1000

            proof_bytes = proof.byte_size()
        finally:
            peak = sampler.stop()

        pkmb = _mb(peak)
        prove_times.append(prove_ms)
        verify_times.append(verify_ms)
        all_valid = all_valid and valid
        peak_mb_max = max(peak_mb_max, pkmb)

        status = "✓" if valid else "✗"
        print(
            f"  {name:<14}  {actual_n:>8,}  {i:>3}  "
            f"{prove_ms:>10.3f}  {verify_ms:>10.3f}  "
            f"{proof_bytes:>8}  {pkmb:>8.2f}  {status}"
        )

    return {
        "name": name,
        "format": label,
        "constraints": actual_n,
        "build_ms": build_ms,
        "file_kb": len(data) / 1024,
        "prove": _stats(prove_times),
        "verify": _stats(verify_times),
        "peak_mb": peak_mb_max,
        "all_valid": all_valid,
    }


def run_precompiled_fallback(size, iterations) -> dict:
    """
    For constraint sizes too large for practical file generation, use
    prove_test_precompiled (internal test circuit, precompiled SRS).
    Clearly labelled in output.
    """
    prove_times = []
    verify_times = []
    peak_mb_max = 0.0
    all_valid = True

    for i in range(1, iterations + 1):
        witness = [1] * (size + 1)
        sampler = _PeakSampler()
        sampler.start()
        try:
            t0 = time.perf_counter()
            proof = y.prove_test_precompiled(size, witness)
            prove_ms = (time.perf_counter() - t0) * 1000

            t0 = time.perf_counter()
            valid = proof.verify_precompiled()
            verify_ms = (time.perf_counter() - t0) * 1000

            proof_bytes = proof.byte_size()
        finally:
            peak = sampler.stop()

        pkmb = _mb(peak)
        prove_times.append(prove_ms)
        verify_times.append(verify_ms)
        all_valid = all_valid and valid
        peak_mb_max = max(peak_mb_max, pkmb)

        status = "✓" if valid else "✗"
        print(
            f"  {'[precompiled]':<14}  {size:>8,}  {i:>3}  "
            f"{prove_ms:>10.3f}  {verify_ms:>10.3f}  "
            f"{proof_bytes:>8}  {pkmb:>8.2f}  {status}"
        )

    return {
        "name": "precompiled",
        "format": "built-in",
        "constraints": size,
        "build_ms": 0.0,
        "file_kb": 0.0,
        "prove": _stats(prove_times),
        "verify": _stats(verify_times),
        "peak_mb": peak_mb_max,
        "all_valid": all_valid,
    }


# ─── main ─────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Test Yoimiya SDK with real programmatic circuits via file-based API."
    )
    parser.add_argument(
        "--sizes",
        nargs="+", type=int,
        default=[100, 500, 1000, 2000, 10000, 50000, 100000, 250000, 500000, 1000000],
        help="Constraint sizes to test.",
    )
    parser.add_argument(
        "--iterations", "-n",
        type=int, default=3,
        help="Prove/verify repetitions per circuit (default: 3).",
    )
    parser.add_argument(
        "--max-file-size",
        type=int, default=50000,
        help="Constraint limit for file-based circuits (default: 50000). "
             "Larger sizes use precompiled fallback.",
    )
    parser.add_argument(
        "--circuits",
        nargs="+",
        default=["fibonacci", "mul-chain", "range-check", "mimc-acir"],
        choices=list(CIRCUIT_DEFS.keys()),
        help="Which circuit types to test (default: all).",
    )
    args = parser.parse_args()

    print()
    print("╔══════════════════════════════════════════════════════════════════════╗")
    print("║         YOIMIYA REAL CIRCUIT TEST — File-based Proving              ║")
    print("╚══════════════════════════════════════════════════════════════════════╝")
    print()

    # -- Section 1: Hardware --------------------------------------------------
    hw = y.hardware_info()
    print("Hardware:")
    print(f"  cores={hw['logical_cores']}  tier={hw['tier']}  "
          f"partitions={hw['partitions']}  threads={hw['total_threads']}")
    print()

    # -- Section 2: File-based circuits ---------------------------------------
    file_sizes = [s for s in args.sizes if s <= args.max_file_size]
    large_sizes = [s for s in args.sizes if s > args.max_file_size]

    all_results = []

    if file_sizes:
        print("=" * 80)
        print(f"FILE-BASED CIRCUITS  (prove_r1cs / prove_acir,  ≤ {args.max_file_size:,} constraints)")
        print("=" * 80)
        print(
            f"  {'circuit':<14}  {'constrs':>8}  {'itr':>3}  "
            f"{'prove_ms':>10}  {'verify_ms':>10}  "
            f"{'proof_B':>8}  {'peak_MB':>8}  {'ok':>2}"
        )
        print("-" * 80)

        with tempfile.TemporaryDirectory() as tmpdir:
            tmp = Path(tmpdir)
            for size in file_sizes:
                for circ_name in args.circuits:
                    result = run_file_circuit(circ_name, size, args.iterations, tmp)
                    all_results.append(result)
                print()

    # -- Section 3: Precompiled fallback for large sizes ----------------------
    if large_sizes:
        print("=" * 80)
        print(f"LARGE SIZES  (prove_test_precompiled — internal test circuit, precompiled SRS)")
        print("=" * 80)
        print(
            f"  {'circuit':<14}  {'constrs':>8}  {'itr':>3}  "
            f"{'prove_ms':>10}  {'verify_ms':>10}  "
            f"{'proof_B':>8}  {'peak_MB':>8}  {'ok':>2}"
        )
        print("-" * 80)

        # Warmup
        print("  Warming up precompiled SRS cache …", end=" ", flush=True)
        _ = y.prove_test_precompiled(large_sizes[0])
        print("done\n")

        for size in large_sizes:
            result = run_precompiled_fallback(size, args.iterations)
            all_results.append(result)
            print()

    # -- Summary --------------------------------------------------------------
    print("=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(
        f"  {'circuit':<14}  {'constrs':>9}  {'format':>8}  "
        f"{'file_kB':>8}  {'prove_avg':>10}  {'verify_avg':>11}  "
        f"{'peak_MB':>8}  {'status':>6}"
    )
    print("-" * 80)
    for r in all_results:
        status = "ALL ✓" if r["all_valid"] else "FAIL ✗"
        p = r["prove"]
        v = r["verify"]
        print(
            f"  {r['name']:<14}  {r['constraints']:>9,}  {r['format']:>8}  "
            f"  {r['file_kb']:>7.1f}  {p['avg']:>9.3f}ms  {v['avg']:>10.3f}ms  "
            f"  {r['peak_mb']:>7.2f}  {status}"
        )
    print()
    print("Real circuit test complete.")


if __name__ == "__main__":
    main()
