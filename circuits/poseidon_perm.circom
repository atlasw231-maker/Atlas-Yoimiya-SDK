pragma circom 2.0.0;

// Poseidon-style permutation: a ZK-friendly hash that uses x^5 S-boxes.
// This circuit runs T permutation rounds, each costing 2 constraints (x^2, x^4*x).
// ROUNDS=250 gives ~500 constraints of genuine non-trivial multiplication gates.

template Pow5(n) {
    signal input in[n];
    signal output out[n];
    signal in2[n];
    signal in4[n];
    for (var i = 0; i < n; i++) {
        in2[i] <== in[i] * in[i];
        in4[i] <== in2[i] * in2[i];
        out[i] <== in4[i] * in[i];
    }
}

template LinearLayer(n) {
    signal input in[n];
    signal output out[n];
    // Simple MDS-style mix: out[i] = sum of in[j] * (j+1) mod n
    var MDS[3][3] = [
        [2, 1, 1],
        [1, 2, 1],
        [1, 1, 2]
    ];
    for (var i = 0; i < n; i++) {
        var s = 0;
        for (var j = 0; j < n; j++) {
            s += MDS[i][j] * in[j];
        }
        out[i] <== s;
    }
}

template PoseidonPerm(ROUNDS) {
    signal input state[3];
    signal output out[3];

    signal s[ROUNDS+1][3];
    s[0][0] <== state[0];
    s[0][1] <== state[1];
    s[0][2] <== state[2];

    component pow5[ROUNDS];
    component lin[ROUNDS];
    for (var r = 0; r < ROUNDS; r++) {
        pow5[r] = Pow5(3);
        lin[r] = LinearLayer(3);
        for (var i = 0; i < 3; i++) {
            pow5[r].in[i] <== s[r][i] + (r * 3 + i + 1);
        }
        for (var i = 0; i < 3; i++) {
            lin[r].in[i] <== pow5[r].out[i];
        }
        for (var i = 0; i < 3; i++) {
            s[r+1][i] <== lin[r].out[i];
        }
    }

    out[0] <== s[ROUNDS][0];
    out[1] <== s[ROUNDS][1];
    out[2] <== s[ROUNDS][2];
}

component main {public [state]} = PoseidonPerm(100);
