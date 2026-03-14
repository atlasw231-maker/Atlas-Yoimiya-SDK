#!/usr/bin/env python3
"""
ACIR and Plonkish circuit tests for Yoimiya SDK.

Exercises the two circuit formats supported by Yoimiya beyond R1CS:
  - ACIR      (.acir)     — opcode-based IR (AssertZero + Mul opcodes)
  - Plonkish  (.plonkish) — gate table format (w[a] × w[b] = w[c])

All circuit files are generated directly in this script — no external
compiler (nargo, halo2) is required. Each generator faithfully implements
the binary format documented in src/circuit.rs.

Circuits:
  ACIR:
    1. inner_product.acir      300 Mul gates       a[i] × b[i] = c[i]
    2. linear_recurrence.acir  199 AssertZero gates w[i+1] - w[i] - 1 = 0
  Plonkish:
    3. mul_grid.plonkish       400 Mul gates        a[i] × b[i] = c[i]
    4. cube_check.plonkish     250 Mul gates        x³ = y  (x×x=x², x²×x=y)

Usage:
    cd "C:\\Users\\Miko De La Paz\\yoimiya-sdk-0.1.0"
    python acir_plonkish_test.py
"""
import sys, os, struct, time

SDK_DIR  = os.path.dirname(os.path.abspath(__file__))
CIRC_DIR = os.path.join(SDK_DIR, "circuits")
os.makedirs(CIRC_DIR, exist_ok=True)

sys.path.insert(0, os.path.join(SDK_DIR, "bindings", "python"))
import yoimiya as y

# BN254 scalar field prime (Fr), per EIP-197 / arkworks bn254
BN254_R = 0x30644e72e131a029b85045b68181585d2833e84879b9709142e1f0121e840101

def green(s): return f"\033[92m{s}\033[0m"
def red(s):   return f"\033[91m{s}\033[0m"
def bold(s):  return f"\033[1m{s}\033[0m"

def fe(v: int) -> bytes:
    """Encode integer as 32-byte LE BN254 field element."""
    return (int(v) % BN254_R).to_bytes(32, 'little')

def fe_neg(v: int) -> bytes:
    """Encode -v mod r as 32-byte LE BN254 field element."""
    return ((BN254_R - int(v) % BN254_R) % BN254_R).to_bytes(32, 'little')


# ─────────────────────────────────────────────────────────────────────────────
#  ACIR Binary Format (src/circuit.rs :: parse_acir_binary)
#
#  Header:
#    num_witnesses (u32 LE)  — wires 0..num_witnesses-1 are user wires;
#                              parser adds one more for constant → num_variables = num_witnesses+1
#    num_public    (u32 LE)
#
#  Opcodes — each starts with a 4-byte u32 opcode tag:
#    0 (AssertZero): opcode(u32) + n_terms(u32) + n × [ wire(u32) + coeff(32 bytes LE) ]
#                    Constraint: (Σ coeff[i]·w[wire[i]]) × w[0] = 0
#                    → satisfiable when Σ coeff[i]·w[wire[i]] = 0  (since w[0]=1)
#    1 (Mul):        opcode(u32) + wire_a(u32) + wire_b(u32) + wire_c(u32)
#                    Constraint: w[wire_a] × w[wire_b] = w[wire_c]
# ─────────────────────────────────────────────────────────────────────────────

def build_inner_product_acir(n: int = 300) -> tuple[bytes, list[int]]:
    """
    Inner product circuit: a[i] × b[i] = c[i]  (n Mul gates).

    Wire layout (1-indexed user wires; wire 0 = constant, unused here):
      w[3i+1] = a[i],  w[3i+2] = b[i],  w[3i+3] = c[i]

    Binary header: num_witnesses = 3n  (→ num_variables = 3n+1)
    Witness array: 3n+1 elements, w[0] unused (0), w[3i+1..3i+3] = a,b,c
    """
    num_witnesses = 3 * n
    buf = bytearray(struct.pack('<II', num_witnesses, 1))   # 1 public input

    witness = [0] * (num_witnesses + 1)     # +1: parser implicit constant slot
    for i in range(n):
        a  = i % 100 + 2    # 2..101
        b  = i % 50  + 3    # 3..52
        c  = a * b           # 6..5252  — fits in u64
        wa, wb, wc = 3*i+1, 3*i+2, 3*i+3
        witness[wa], witness[wb], witness[wc] = a, b, c
        buf += struct.pack('<IIII', 1, wa, wb, wc)      # Mul opcode (u32=1)

    return bytes(buf), witness


def build_linear_recurrence_acir(n: int = 200) -> tuple[bytes, list[int]]:
    """
    Arithmetic progression check: w[i+1] - w[i] - 1 = 0  (n-1 AssertZero gates).

    Wire layout:
      w[0] = 1  (constant — referenced by AssertZero's implicit b=[(0,1)] row)
      w[i] = i  for i in 1..n   (the progression 1, 2, 3, ..., n)

    Each constraint: (w[i+1]·(+1)) + (w[i]·(-1)) + (w[0]·(-1)) = 0
                   = (i+1) - i - 1 = 0  ✓

    Binary header: num_witnesses = n  (→ num_variables = n+1)
    Witness array: n+1 elements: [1, 1, 2, 3, ..., n]
    """
    num_witnesses = n
    buf = bytearray(struct.pack('<II', num_witnesses, 1))

    # Witness: w[0]=1 (constant), w[i]=i for i in 1..n
    witness = [0] * (num_witnesses + 1)
    witness[0] = 1
    for i in range(1, n + 1):
        witness[i] = i

    pos1 = fe(1)
    neg1 = fe_neg(1)

    for i in range(1, n):   # 199 constraints: i = 1..n-1
        buf += struct.pack('<II', 0, 3)                     # AssertZero, 3 terms
        buf += struct.pack('<I', i + 1) + pos1              # +w[i+1]
        buf += struct.pack('<I', i)     + neg1              # -w[i]
        buf += struct.pack('<I', 0)     + neg1              # -w[0] = -1

    return bytes(buf), witness


# ─────────────────────────────────────────────────────────────────────────────
#  Plonkish Binary Format (src/circuit.rs :: parse_plonkish_binary)
#
#  Header:
#    num_rows   (u32 LE) — one row per gate
#    num_cols   (u32 LE) — wire columns (used to compute num_variables)
#    num_public (u32 LE)
#
#  Gate rows — num_rows × 20 bytes each:
#    wire_a (u32 LE) + wire_b (u32 LE) + wire_c (u32 LE) + q_m (u32 LE) + q_c (u32 LE)
#    Constraint: w[wire_a] × w[wire_b] = w[wire_c]
#
#  num_variables = num_rows × num_cols + 1   (wire 0 = constant, rest are gate wires)
# ─────────────────────────────────────────────────────────────────────────────

def build_mul_grid_plonkish(n: int = 400) -> tuple[bytes, list[int]]:
    """
    Multiplication grid: a[i] × b[i] = c[i]  (n Plonkish Mul gates).

    Gate i: wire_a = 3i+1, wire_b = 3i+2, wire_c = 3i+3  (num_cols = 3)
    num_variables = 3n+1;  max wire index = 3(n-1)+3 = 3n−0 ≤ 3n ✓

    Witness: w[0]=1, w[3i+1]=a, w[3i+2]=b, w[3i+3]=a×b
    """
    buf = bytearray(struct.pack('<III', n, 3, 1))   # rows, cols, public

    num_vars = n * 3 + 1
    witness  = [0] * num_vars
    witness[0] = 1

    for i in range(n):
        a  = i % 17 + 2     # 2..18
        b  = i % 13 + 3     # 3..15
        c  = a * b           # 6..270  — fits in u64
        wa, wb, wc = 3*i+1, 3*i+2, 3*i+3
        witness[wa], witness[wb], witness[wc] = a, b, c
        buf += struct.pack('<IIIII', wa, wb, wc, 1, 0)   # q_m=1

    return bytes(buf), witness


def build_cube_check_plonkish(n: int = 125) -> tuple[bytes, list[int]]:
    """
    Cube check: x[i]³ = y[i] verified in two consecutive gates per element.
    Gate 2i  : wire_a=x, wire_b=x, wire_c=x² → x × x   = x²
    Gate 2i+1: wire_a=x², wire_b=x, wire_c=y → x² × x  = x³ = y

    n elements → 2n total gates, num_cols=3
    num_variables = 2n×3+1 = 6n+1;  max wire index = 3(n-1)+3 = 3n−0 ≤ 6n ✓

    Witness: w[0]=1, w[3i+1]=x, w[3i+2]=x², w[3i+3]=x³
    x∈[2,11] → x³∈[8,1331] — all values fit in u64.
    """
    num_rows = 2 * n
    buf = bytearray(struct.pack('<III', num_rows, 3, 1))

    num_vars = num_rows * 3 + 1
    witness  = [0] * num_vars

    for i in range(n):
        x   = i % 10 + 2    # 2..11
        x2  = x * x          # 4..121
        y   = x2 * x         # 8..1331
        wx, wx2, wy = 3*i+1, 3*i+2, 3*i+3
        witness[wx], witness[wx2], witness[wy] = x, x2, y
        buf += struct.pack('<IIIII', wx,  wx,  wx2, 1, 0)   # x×x=x²
        buf += struct.pack('<IIIII', wx2, wx,  wy,  1, 0)   # x²×x=y

    return bytes(buf), witness


# ─────────────────────────────────────────────────────────────────────────────
#  Test runner
# ─────────────────────────────────────────────────────────────────────────────

def run_test(label: str, path: str, circuit_bytes: bytes, witness: list[int],
             num_constraints: int, prove_fn) -> bool:
    """Write circuit file, prove, verify, print result."""
    with open(path, 'wb') as f:
        f.write(circuit_bytes)

    # Add 15% + 32 headroom so a slightly different total constraint count doesn't fail
    srs = y.generate_test_srs(int(num_constraints * 1.15) + 32)

    t0 = time.perf_counter()
    proof = prove_fn(path, witness, srs)
    prove_ms = (time.perf_counter() - t0) * 1000

    t1 = time.perf_counter()
    ok = proof.verify(srs)
    verify_ms = (time.perf_counter() - t1) * 1000

    status = green("PASS") if ok else red("FAIL")
    print(f"  [{status}] {label:45s}  prove={prove_ms:7.1f}ms  verify={verify_ms:6.1f}ms")
    return ok


def main():
    print(bold("\n=== Yoimiya ACIR + Plonkish Circuit Test ===\n"))

    results = []

    # ── ACIR ──────────────────────────────────────────────────────────────────
    print(bold("Format: ACIR (.acir)"))
    print("  Binary format: num_witnesses(u32) + num_public(u32) + opcodes")
    print("  Opcode 0 = AssertZero  Σ coeff[i]·w[i] = 0  (32-byte LE field coefficients)")
    print("  Opcode 1 = Mul         w[a] × w[b] = w[c]")
    print()

    # ACIR 1: inner product (Mul gates)
    data, wit = build_inner_product_acir(300)
    path = os.path.join(CIRC_DIR, "inner_product.acir")
    print(f"  Circuit: inner_product.acir")
    print(f"    300 Mul gates — a[i] × b[i] = c[i]  (a∈[2,101], b∈[3,52])")
    print(f"    Witnesses: {len(wit)}  (max value 5252, u64-safe)")
    ok = run_test("inner_product.acir  [300 Mul]",
                  path, data, wit, 300, y.prove_acir)
    results.append(("inner_product.acir    (ACIR, Mul)",         ok))

    print()

    # ACIR 2: linear recurrence (AssertZero gates)
    data, wit = build_linear_recurrence_acir(200)
    path = os.path.join(CIRC_DIR, "linear_recurrence.acir")
    print(f"  Circuit: linear_recurrence.acir")
    print(f"    199 AssertZero gates — w[i+1] - w[i] - 1 = 0  (±1 field coefficients)")
    print(f"    Witnesses: {len(wit)}  (values 0..200, u64-safe)")
    ok = run_test("linear_recurrence.acir [199 AssertZero]",
                  path, data, wit, 200, y.prove_acir)
    results.append(("linear_recurrence.acir (ACIR, AssertZero)", ok))

    # ── Plonkish ──────────────────────────────────────────────────────────────
    print()
    print(bold("Format: Plonkish (.plonkish)"))
    print("  Binary format: num_rows(u32) + num_cols(u32) + num_public(u32) + gate rows")
    print("  Each gate row (20 bytes): wire_a + wire_b + wire_c + q_m + q_c")
    print("  Constraint: w[wire_a] × w[wire_b] = w[wire_c]")
    print()

    # Plonkish 1: mul grid
    data, wit = build_mul_grid_plonkish(400)
    path = os.path.join(CIRC_DIR, "mul_grid.plonkish")
    print(f"  Circuit: mul_grid.plonkish")
    print(f"    400 Mul gates — a[i] × b[i] = c[i]  (a∈[2,18], b∈[3,15])")
    print(f"    Witnesses: {len(wit)}  (max value 270, u64-safe)")
    ok = run_test("mul_grid.plonkish   [400 Mul]",
                  path, data, wit, 400, y.prove_plonkish)
    results.append(("mul_grid.plonkish   (Plonkish, Mul)",        ok))

    print()

    # Plonkish 2: cube check (x^3=y via paired gates)
    data, wit = build_cube_check_plonkish(125)
    path = os.path.join(CIRC_DIR, "cube_check.plonkish")
    print(f"  Circuit: cube_check.plonkish")
    print(f"    250 Mul gates — x³=y checked via x×x=x², x²×x=y  (x∈[2,11])")
    print(f"    Witnesses: {len(wit)}  (max value 1331, u64-safe)")
    ok = run_test("cube_check.plonkish [250 Mul, x³=y]",
                  path, data, wit, 250, y.prove_plonkish)
    results.append(("cube_check.plonkish (Plonkish, x³=y)",       ok))

    # ── Summary ───────────────────────────────────────────────────────────────
    print()
    print(bold("=== Summary ==="))
    all_pass = True
    for name, ok in results:
        status = green("PASS") if ok else red("FAIL")
        print(f"  [{status}] {name}")
        all_pass = all_pass and ok

    print()
    if all_pass:
        print(green("All tests PASSED — ACIR and Plonkish circuits proved and verified."))
    else:
        print(red("Some tests FAILED."))
        sys.exit(1)


if __name__ == "__main__":
    main()
