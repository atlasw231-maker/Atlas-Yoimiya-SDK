pragma circom 2.0.0;

// Range proof: prove that a secret value is in [0, 2^BITS).
// This uses standard bit decomposition — the classic pattern in
// production circuits (Tornado Cash, zkSync, Semaphore, etc).
// Each bit costs 1 constraint: b * (b - 1) = 0.
// Then we verify the reconstruction: sum(b[i] * 2^i) = value.
// Total: BITS + 1 constraints.

template Num2Bits(n) {
    signal input in;
    signal output out[n];
    var lc1 = 0;
    var e2 = 1;
    for (var i = 0; i < n; i++) {
        out[i] <-- (in >> i) & 1;
        out[i] * (out[i] - 1) === 0;   // boolean check: 1 constraint per bit
        lc1 += out[i] * e2;
        e2 = e2 + e2;
    }
    lc1 === in;   // reconstruction check: 1 constraint
}

template RangeProof(BITS) {
    signal input value;      // private: the secret value
    signal input max_value;  // public: the upper bound

    // Prove value < 2^BITS
    component n2b = Num2Bits(BITS);
    n2b.in <== value;

    // Also prove (max_value - value) has a valid BITS-bit representation
    // i.e., value <= max_value
    signal diff;
    diff <== max_value - value;
    component n2b2 = Num2Bits(BITS);
    n2b2.in <== diff;
}

// 32-bit range proof: 65 constraints (32 bits × 2 decompositions + 2 reconstruction checks)
component main {public [max_value]} = RangeProof(32);
