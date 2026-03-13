/**
 * Yoimiya ZK Proving SDK - TypeScript Type Definitions
 */

/**
 * Structured Reference String for proving and verification
 */
export class Srs {
  /**
   * Generate a deterministic test SRS
   * @param maxDegree - Maximum polynomial degree the SRS supports
   */
  constructor(maxDegree: number);
  
  /**
   * Free the SRS resources
   */
  destroy(): void;
}

/**
 * Zero-knowledge proof
 */
export class Proof {
  /**
   * Verify this proof
   * @param srs - The SRS used for proving
   * @returns true if valid, false otherwise
   */
  verify(srs: Srs): boolean;

  /**
   * Return compressed serialized proof size in bytes
   */
  byteSize(): number;
  
  /**
   * Free the proof resources
   */
  destroy(): void;
}

/**
 * Aggregated batch proof
 */
export class BatchProof {
  /**
   * Verify this batch proof
   * @param srs - The SRS used for proving
   * @returns true if valid, false otherwise
   */
  verify(srs: Srs): boolean;

  /**
   * Serialize this batch proof to calldata bytes
   */
  toCalldata(): Buffer;
  
  /**
   * Free the batch proof resources
   */
  destroy(): void;
}

/**
 * Generate a deterministic test SRS
 * @param maxDegree - Maximum polynomial degree
 * @returns Srs object
 */
export function generateTestSrs(maxDegree: number): Srs;

/**
 * Prove a test circuit
 * @param numConstraints - Number of R1CS constraints
 * @param witness - Array of witness values (64-bit integers)
 * @param srs - Structured Reference String
 * @returns Proof object
 */
export function proveTest(numConstraints: number, witness: number[], srs: Srs): Proof;

/**
 * Prove an R1CS circuit
 * @param r1csPath - Path to the .r1cs file
 * @param witness - Array of witness values (64-bit integers)
 * @param srs - Structured Reference String
 * @returns Proof object
 */
export function proveR1cs(r1csPath: string, witness: number[], srs: Srs): Proof;

/**
 * Aggregate multiple proofs into a single batch proof
 * @param proofs - Array of Proof objects
 * @param srs - Structured Reference String
 * @returns BatchProof object
 */
export function aggregateProofs(proofs: Proof[], srs: Srs): BatchProof;
