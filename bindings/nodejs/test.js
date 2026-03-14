/**
 * Yoimiya Node.js Binding Tests
 *
 * Exercises the full binding surface: SRS generation, proveTest,
 * proveR1cs, aggregation, batch verification, and calldata serialization.
 *
 * Run with:  node test.js
 * Or via:    npm test  (from bindings/nodejs/)
 */

'use strict';

const path = require('path');
const { generateTestSrs, proveTest, proveR1cs, aggregateProofs } = require('./index.js');

// ─── helpers ─────────────────────────────────────────────────────────────────

let passed = 0;
let failed = 0;

function run(name, fn) {
  process.stdout.write(`  ${name} ... `);
  const t0 = performance.now();
  try {
    fn();
    const ms = (performance.now() - t0).toFixed(2);
    console.log(`PASS (${ms} ms)`);
    passed++;
  } catch (err) {
    console.log(`FAIL\n    ${err.message}`);
    failed++;
  }
}

function assert(cond, msg) {
  if (!cond) throw new Error(msg || 'assertion failed');
}

// ─── tests ───────────────────────────────────────────────────────────────────

console.log('\nYoimiya Node.js binding tests\n');

// 1. SRS generation
let srs;
run('generate_test_srs(2048)', () => {
  srs = generateTestSrs(2048);
  assert(srs && srs.handle, 'SRS handle is null');
});

// 2. Basic proof generation + verification
run('proveTest 100 constraints', () => {
  const witness = Array.from({ length: 101 }, () => 1n);
  const proof = proveTest(100, witness, srs);
  assert(proof && proof.handle, 'proof handle is null');
  const valid = proof.verify(srs);
  assert(valid === true, `verify returned ${valid}`);
  proof.destroy();
});

run('proveTest 500 constraints', () => {
  const witness = Array.from({ length: 501 }, () => 1n);
  const proof = proveTest(500, witness, srs);
  assert(proof.handle, 'proof handle is null');
  assert(proof.verify(srs) === true, 'proof not valid');
  proof.destroy();
});

run('proveTest 1000 constraints', () => {
  const witness = Array.from({ length: 1001 }, () => 1n);
  const proof = proveTest(1000, witness, srs);
  assert(proof.handle, 'proof handle is null');
  assert(proof.verify(srs) === true, 'proof not valid');
  proof.destroy();
});

// 3. Proof byte size
run('proof_size_bytes is positive', () => {
  const witness = Array.from({ length: 201 }, () => 1n);
  const proof = proveTest(200, witness, srs);
  const size = proof.byteSize();
  assert(size > 0, `expected positive size, got ${size}`);
  proof.destroy();
});

// 4. R1CS circuit — use the bundled test circuit
const r1csPath = path.resolve(__dirname, '../../assets/release/test_circuit.r1cs');
run('proveR1cs test_circuit.r1cs', () => {
  const witness = Array.from({ length: 12 }, () => 1n);
  const proof = proveR1cs(r1csPath, witness, srs);
  assert(proof && proof.handle, 'R1CS proof handle is null');
  assert(proof.verify(srs) === true, 'R1CS proof not valid');
  proof.destroy();
});

// 5. Aggregation of 2 proofs
run('aggregateProofs 2 proofs', () => {
  const w = Array.from({ length: 301 }, () => 1n);
  const p1 = proveTest(300, w, srs);
  const p2 = proveTest(300, w, srs);
  const batch = aggregateProofs([p1, p2], srs);
  assert(batch && batch.handle, 'batch handle is null');
  assert(batch.verify(srs) === true, 'batch not valid');
  p1.destroy();
  p2.destroy();
  batch.destroy();
});

// 6. Aggregation of 5 proofs
run('aggregateProofs 5 proofs', () => {
  const proofs = [];
  for (let i = 0; i < 5; i++) {
    const sz = 100 + i * 50;
    const w = Array.from({ length: sz + 1 }, () => 1n);
    proofs.push(proveTest(sz, w, srs));
  }
  const batch = aggregateProofs(proofs, srs);
  assert(batch && batch.handle, 'batch handle is null');
  assert(batch.verify(srs) === true, 'batch not valid');
  proofs.forEach(p => p.destroy());
  batch.destroy();
});

// 7. Batch calldata serialization
run('batch.toCalldata() produces 275 bytes', () => {
  const w = Array.from({ length: 101 }, () => 1n);
  const p1 = proveTest(100, w, srs);
  const p2 = proveTest(100, w, srs);
  const batch = aggregateProofs([p1, p2], srs);
  const calldata = batch.toCalldata();
  assert(Buffer.isBuffer(calldata), 'expected Buffer');
  assert(calldata.length === 275, `expected 275 bytes, got ${calldata.length}`);
  p1.destroy();
  p2.destroy();
  batch.destroy();
});

// 8. Witness too short should throw
run('proveTest throws on short witness', () => {
  let threw = false;
  try {
    proveTest(500, [1n, 2n], srs); // only 2 elements for 500 constraints
  } catch (e) {
    threw = true;
  }
  assert(threw, 'expected error for undersized witness');
});

// ─── summary ─────────────────────────────────────────────────────────────────

srs.destroy();

console.log(`\n${passed + failed} tests: ${passed} passed, ${failed} failed`);

if (failed > 0) {
  process.exit(1);
}
