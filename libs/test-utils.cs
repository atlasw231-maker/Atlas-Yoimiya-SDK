using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.Linq;

namespace Yoimiya.TestUtils
{
    /// <summary>
    /// High-level interface for testing Yoimiya SDK functionality
    /// Provides utilities for testing proofs, verifications, and batch operations
    /// </summary>
    public class YoimiyaTester
    {
        private readonly YoimiyaSdk.Srs _srs;
        private readonly int _maxDegree;
        private readonly List<TestResult> _testResults;

        /// <summary>
        /// Initialize tester with SRS
        /// </summary>
        public YoimiyaTester(int maxDegree = 2048)
        {
            _maxDegree = maxDegree;
            _srs = YoimiyaSdk.GenerateTestSrs(maxDegree);
            _testResults = new List<TestResult>();
        }

        /// <summary>
        /// Test basic proof generation and verification
        /// </summary>
        public TestResult TestSimpleProof(int numConstraints = 100, byte[] witness = null)
        {
            if (witness == null)
            {
                witness = new byte[] { 1, 2, 3, 4 };
            }

            var result = new TestResult
            {
                Test = "simple_proof",
                Constraints = numConstraints,
                Status = "FAILED"
            };

            try
            {
                // Measure proof generation time
                var sw = Stopwatch.StartNew();
                var proof = YoimiyaSdk.ProveTest(numConstraints, witness, _srs);
                sw.Stop();
                var proveMs = sw.Elapsed.TotalMilliseconds;

                // Measure verification time
                sw.Restart();
                var valid = proof.Verify(_srs);
                sw.Stop();
                var verifyMs = sw.Elapsed.TotalMilliseconds;

                result.Status = valid ? "PASSED" : "FAILED";
                result.ProveMs = Math.Round(proveMs, 4);
                result.VerifyMs = Math.Round(verifyMs, 4);
                result.ProofValid = valid;
            }
            catch (Exception ex)
            {
                result.Error = ex.Message;
            }

            _testResults.Add(result);
            return result;
        }

        /// <summary>
        /// Test proof aggregation and batch verification
        /// </summary>
        public TestResult TestBatchAggregation(int numProofs = 5, int constraintsPerProof = 100, byte[] witness = null)
        {
            if (witness == null)
            {
                witness = new byte[] { 1, 2, 3, 4 };
            }

            var result = new TestResult
            {
                Test = "batch_aggregation",
                NumProofs = numProofs,
                ConstraintsPerProof = constraintsPerProof,
                Status = "FAILED"
            };

            try
            {
                // Generate multiple proofs
                var proofs = new List<YoimiyaSdk.Proof>();
                for (int i = 0; i < numProofs; i++)
                {
                    var proof = YoimiyaSdk.ProveTest(constraintsPerProof, witness, _srs);
                    proofs.Add(proof);
                }

                // Measure aggregation time
                var sw = Stopwatch.StartNew();
                var batchProof = YoimiyaSdk.AggregateProofs(proofs.ToArray(), _srs);
                sw.Stop();
                var aggregateMs = sw.Elapsed.TotalMilliseconds;

                // Measure batch verification time
                sw.Restart();
                var valid = batchProof.Verify(_srs);
                sw.Stop();
                var verifyMs = sw.Elapsed.TotalMilliseconds;

                result.Status = valid ? "PASSED" : "FAILED";
                result.AggregateMs = Math.Round(aggregateMs, 4);
                result.BatchVerifyMs = Math.Round(verifyMs, 4);
                result.BatchValid = valid;
            }
            catch (Exception ex)
            {
                result.Error = ex.Message;
            }

            _testResults.Add(result);
            return result;
        }

        /// <summary>
        /// Test proof generation across different constraint sizes
        /// </summary>
        public List<TestResult> TestScalability(int[] constraintSizes = null)
        {
            if (constraintSizes == null)
            {
                constraintSizes = new[] { 100, 500, 1000, 2000 };
            }

            var results = new List<TestResult>();
            foreach (var size in constraintSizes)
            {
                var result = TestSimpleProof(size, new byte[] { 1, 2, 3, 4 });
                results.Add(result);
            }

            return results;
        }

        /// <summary>
        /// Test proof generation with large constraint counts (up to 1M)
        /// Useful for developers to understand performance at scale and identify
        /// optimal parameters for their use case.
        /// </summary>
        public List<TestResult> TestLargeConstraints(int[] constraintSizes = null)
        {
            if (constraintSizes == null)
            {
                constraintSizes = new[] { 10_000, 50_000, 100_000, 250_000, 500_000, 1_000_000 };
            }

            Console.WriteLine("\nTesting Large Constraint Sizes (up to 1M)...");
            Console.WriteLine(new string('-', 60));

            var results = new List<TestResult>();
            foreach (var size in constraintSizes)
            {
                Console.Write($"  Testing {size:N0} constraints... ");
                var result = TestSimpleProof(size, new byte[] { 1, 2, 3, 4 });
                if (result.Status == "PASSED")
                {
                    Console.WriteLine($"✓ Prove: {result.ProveMs}ms, Verify: {result.VerifyMs}ms");
                }
                else
                {
                    Console.WriteLine($"✗ Failed: {result.Error ?? "Unknown error"}");
                }
                results.Add(result);
            }

            return results;
        }

        /// <summary>
        /// Test aggregation with different batch sizes
        /// </summary>
        public List<TestResult> TestBatchSizes(int[] batchSizes = null, int constraintsPerProof = 100)
        {
            if (batchSizes == null)
            {
                batchSizes = new[] { 2, 5, 10, 20 };
            }

            var results = new List<TestResult>();
            foreach (var batchSize in batchSizes)
            {
                var result = TestBatchAggregation(batchSize, constraintsPerProof);
                results.Add(result);
            }

            return results;
        }

        /// <summary>
        /// Run comprehensive test suite
        /// </summary>
        public TestSuiteResult RunFullTestSuite()
        {
            Console.WriteLine("Running Yoimiya Test Suite...");
            Console.WriteLine(new string('=', 60));

            // Test 1: Simple proofs
            Console.WriteLine("\n[1/4] Testing simple proof generation and verification...");
            var simpleResults = TestScalability(new[] { 100, 500, 1000, 2000 });

            // Test 2: Batch aggregation
            Console.WriteLine("[2/4] Testing batch aggregation...");
            var batchResults = TestBatchSizes(new[] { 2, 5, 10 });

            // Test 3: Large batch
            Console.WriteLine("[3/4] Testing large batch (100 proofs)...");
            var largeBatch = TestBatchAggregation(100, 100);

            // Test 4: Stress test
            Console.WriteLine("[4/4] Testing high-constraint proof...");
            var stressTest = TestSimpleProof(5000, new byte[] { 1, 2, 3, 4 });

            // Print summary
            PrintSummary();

            return new TestSuiteResult
            {
                Simple = simpleResults,
                Batches = batchResults,
                LargeBatch = largeBatch,
                Stress = stressTest
            };
        }

        /// <summary>
        /// Print test results summary
        /// </summary>
        private void PrintSummary()
        {
            Console.WriteLine("\n" + new string('=', 60));
            Console.WriteLine("TEST SUMMARY");
            Console.WriteLine(new string('=', 60));

            var passed = _testResults.Count(r => r.Status == "PASSED");
            var failed = _testResults.Count(r => r.Status == "FAILED");

            Console.WriteLine($"\nTotal tests: {_testResults.Count}");
            Console.WriteLine($"✓ Passed: {passed}");
            Console.WriteLine($"✗ Failed: {failed}");

            Console.WriteLine("\nDetailed Results:");
            Console.WriteLine(new string('-', 60));
            foreach (var result in _testResults)
            {
                var status = result.Status == "PASSED" ? "✓" : "✗";
                var testName = result.Test ?? "unknown";

                if (testName == "simple_proof")
                {
                    Console.WriteLine($"{status} {testName.PadEnd(20)} | Constraints: {result.Constraints.ToString().PadEnd(6)} | " +
                        $"Prove: {result.ProveMs}ms | Verify: {result.VerifyMs}ms");
                }
                else if (testName == "batch_aggregation")
                {
                    Console.WriteLine($"{status} {testName.PadEnd(20)} | Proofs: {result.NumProofs.ToString().PadEnd(6)} | " +
                        $"Aggregate: {result.AggregateMs}ms | Verify: {result.BatchVerifyMs}ms");
                }
            }
        }
    }

    /// <summary>
    /// Individual test result
    /// </summary>
    public class TestResult
    {
        public string Test { get; set; }
        public string Status { get; set; }
        public int Constraints { get; set; }
        public int NumProofs { get; set; }
        public int ConstraintsPerProof { get; set; }
        public double ProveMs { get; set; }
        public double VerifyMs { get; set; }
        public double AggregateMs { get; set; }
        public double BatchVerifyMs { get; set; }
        public bool ProofValid { get; set; }
        public bool BatchValid { get; set; }
        public string Error { get; set; }
    }

    /// <summary>
    /// Full test suite result
    /// </summary>
    public class TestSuiteResult
    {
        public List<TestResult> Simple { get; set; }
        public List<TestResult> Batches { get; set; }
        public TestResult LargeBatch { get; set; }
        public TestResult Stress { get; set; }
    }

    /// <summary>
    /// Quick test utility
    /// </summary>
    public static class QuickTest
    {
        public static TestResult Run()
        {
            Console.WriteLine("Running quick sanity check...");
            var tester = new YoimiyaTester(1024);
            var result = tester.TestSimpleProof(100);

            if (result.Status == "PASSED")
            {
                Console.WriteLine($"✓ SDK is working! Proof generation: {result.ProveMs}ms, " +
                    $"Verification: {result.VerifyMs}ms");
            }
            else
            {
                Console.WriteLine("✗ SDK test failed!");
                if (!string.IsNullOrEmpty(result.Error))
                {
                    Console.WriteLine($"Error: {result.Error}");
                }
            }

            return result;
        }
    }
}
