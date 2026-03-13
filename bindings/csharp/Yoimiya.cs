using System;
using System.Runtime.InteropServices;
using System.Collections.Generic;

namespace Yoimiya.SDK
{
    /// <summary>
    /// C# Bindings for Yoimiya ZK Proving SDK
    /// </summary>
    public static class YoimiyaNative
    {
        // Platform-specific library loading
        private const string LibName = "yoimiya";
        
        // Opaque types
        [StructLayout(LayoutKind.Sequential)]
        public struct YoimiyaSrs
        {
            private IntPtr _ptr;
        }
        
        [StructLayout(LayoutKind.Sequential)]
        public struct YoimiyaProof
        {
            private IntPtr _ptr;
        }
        
        [StructLayout(LayoutKind.Sequential)]
        public struct YoimiyaBatchProof
        {
            private IntPtr _ptr;
        }
        
        // P/Invoke declarations
        
        /// <summary>SRS Management</summary>
        [DllImport(LibName, CallingConvention = CallingConvention.Cdecl)]
        public static extern IntPtr yoimiya_generate_test_srs(uint maxDegree);
        
        [DllImport(LibName, CallingConvention = CallingConvention.Cdecl)]
        public static extern void yoimiya_free_srs(IntPtr srs);
        
        /// <summary>Proving</summary>
        [DllImport(LibName, CallingConvention = CallingConvention.Cdecl)]
        public static extern IntPtr yoimiya_prove_test(
            uint numConstraints,
            ulong[] witnessData,
            uint witnessLen,
            IntPtr srs
        );
        
        [DllImport(LibName, CallingConvention = CallingConvention.Cdecl)]
        public static extern IntPtr yoimiya_prove_r1cs(
            string r1csPath,
            ulong[] witnessData,
            uint witnessLen,
            IntPtr srs
        );
        
        [DllImport(LibName, CallingConvention = CallingConvention.Cdecl)]
        public static extern void yoimiya_free_proof(IntPtr proof);
        
        /// <summary>Verification</summary>
        [DllImport(LibName, CallingConvention = CallingConvention.Cdecl)]
        public static extern int yoimiya_verify(IntPtr proof, IntPtr srs);
        
        /// <summary>Aggregation</summary>
        [DllImport(LibName, CallingConvention = CallingConvention.Cdecl)]
        public static extern IntPtr yoimiya_aggregate(
            IntPtr[] proofs,
            uint count,
            IntPtr srs
        );
        
        [DllImport(LibName, CallingConvention = CallingConvention.Cdecl)]
        public static extern void yoimiya_free_batch_proof(IntPtr batchProof);
        
        [DllImport(LibName, CallingConvention = CallingConvention.Cdecl)]
        public static extern int yoimiya_verify_batch(IntPtr batchProof, IntPtr srs);
    }
    
    /// <summary>
    /// Wrapper class for Structured Reference String
    /// </summary>
    public class Srs : IDisposable
    {
        private IntPtr _handle;
        private bool _disposed = false;
        
        /// <summary>
        /// Generate a deterministic test SRS
        /// </summary>
        /// <param name="maxDegree">Maximum polynomial degree</param>
        public Srs(uint maxDegree)
        {
            _handle = YoimiyaNative.yoimiya_generate_test_srs(maxDegree);
            if (_handle == IntPtr.Zero)
            {
                throw new InvalidOperationException("Failed to generate SRS");
            }
        }
        
        /// <summary>
        /// Get the underlying handle
        /// </summary>
        public IntPtr Handle
        {
            get
            {
                if (_disposed)
                    throw new ObjectDisposedException(nameof(Srs));
                return _handle;
            }
        }
        
        public void Dispose()
        {
            if (!_disposed)
            {
                if (_handle != IntPtr.Zero)
                {
                    YoimiyaNative.yoimiya_free_srs(_handle);
                    _handle = IntPtr.Zero;
                }
                _disposed = true;
                GC.SuppressFinalize(this);
            }
        }
        
        ~Srs()
        {
            Dispose();
        }
    }
    
    /// <summary>
    /// Wrapper class for zero-knowledge proof
    /// </summary>
    public class Proof : IDisposable
    {
        private IntPtr _handle;
        private bool _disposed = false;
        
        internal Proof(IntPtr handle)
        {
            if (handle == IntPtr.Zero)
                throw new ArgumentException("Invalid proof handle");
            _handle = handle;
        }
        
        /// <summary>
        /// Verify the proof
        /// </summary>
        /// <param name="srs">The SRS used for proving</param>
        /// <returns>true if valid, false otherwise</returns>
        public bool Verify(Srs srs)
        {
            if (_disposed)
                throw new ObjectDisposedException(nameof(Proof));
            if (srs == null)
                throw new ArgumentNullException(nameof(srs));
            
            int result = YoimiyaNative.yoimiya_verify(_handle, srs.Handle);
            if (result == -1)
                throw new InvalidOperationException("Verification error");
            return result == 1;
        }
        
        public void Dispose()
        {
            if (!_disposed)
            {
                if (_handle != IntPtr.Zero)
                {
                    YoimiyaNative.yoimiya_free_proof(_handle);
                    _handle = IntPtr.Zero;
                }
                _disposed = true;
                GC.SuppressFinalize(this);
            }
        }
        
        ~Proof()
        {
            Dispose();
        }
    }
    
    /// <summary>
    /// Wrapper class for aggregated batch proof
    /// </summary>
    public class BatchProof : IDisposable
    {
        private IntPtr _handle;
        private bool _disposed = false;
        
        internal BatchProof(IntPtr handle)
        {
            if (handle == IntPtr.Zero)
                throw new ArgumentException("Invalid batch proof handle");
            _handle = handle;
        }
        
        /// <summary>
        /// Verify the batch proof
        /// </summary>
        /// <param name="srs">The SRS used for proving</param>
        /// <returns>true if valid, false otherwise</returns>
        public bool Verify(Srs srs)
        {
            if (_disposed)
                throw new ObjectDisposedException(nameof(BatchProof));
            if (srs == null)
                throw new ArgumentNullException(nameof(srs));
            
            int result = YoimiyaNative.yoimiya_verify_batch(_handle, srs.Handle);
            if (result == -1)
                throw new InvalidOperationException("Batch verification error");
            return result == 1;
        }
        
        public void Dispose()
        {
            if (!_disposed)
            {
                if (_handle != IntPtr.Zero)
                {
                    YoimiyaNative.yoimiya_free_batch_proof(_handle);
                    _handle = IntPtr.Zero;
                }
                _disposed = true;
                GC.SuppressFinalize(this);
            }
        }
        
        ~BatchProof()
        {
            Dispose();
        }
    }
    
    /// <summary>
    /// Public API
    /// </summary>
    public static class YoimiyaSdk
    {
        /// <summary>
        /// Generate a deterministic test SRS
        /// </summary>
        public static Srs GenerateTestSrs(uint maxDegree)
        {
            return new Srs(maxDegree);
        }
        
        /// <summary>
        /// Prove a test circuit
        /// </summary>
        public static Proof ProveTest(uint numConstraints, ulong[] witness, Srs srs)
        {
            if (srs == null)
                throw new ArgumentNullException(nameof(srs));
            if (witness == null)
                throw new ArgumentNullException(nameof(witness));
            
            IntPtr proofHandle = YoimiyaNative.yoimiya_prove_test(
                numConstraints,
                witness,
                (uint)witness.Length,
                srs.Handle
            );
            
            if (proofHandle == IntPtr.Zero)
                throw new InvalidOperationException("Failed to prove");
            
            return new Proof(proofHandle);
        }
        
        /// <summary>
        /// Prove an R1CS circuit
        /// </summary>
        public static Proof ProveR1cs(string r1csPath, ulong[] witness, Srs srs)
        {
            if (srs == null)
                throw new ArgumentNullException(nameof(srs));
            if (witness == null)
                throw new ArgumentNullException(nameof(witness));
            if (string.IsNullOrEmpty(r1csPath))
                throw new ArgumentException("Invalid R1CS path", nameof(r1csPath));
            
            IntPtr proofHandle = YoimiyaNative.yoimiya_prove_r1cs(
                r1csPath,
                witness,
                (uint)witness.Length,
                srs.Handle
            );
            
            if (proofHandle == IntPtr.Zero)
                throw new InvalidOperationException("Failed to prove R1CS");
            
            return new Proof(proofHandle);
        }
        
        /// <summary>
        /// Aggregate multiple proofs
        /// </summary>
        public static BatchProof AggregateProofs(List<Proof> proofs, Srs srs)
        {
            if (srs == null)
                throw new ArgumentNullException(nameof(srs));
            if (proofs == null || proofs.Count == 0)
                throw new ArgumentException("No proofs to aggregate", nameof(proofs));
            
            IntPtr[] proofHandles = new IntPtr[proofs.Count];
            for (int i = 0; i < proofs.Count; i++)
            {
                // Extract handle (would need accessor in Proof class)
                proofHandles[i] = IntPtr.Zero; // Placeholder
            }
            
            IntPtr batchHandle = YoimiyaNative.yoimiya_aggregate(
                proofHandles,
                (uint)proofs.Count,
                srs.Handle
            );
            
            if (batchHandle == IntPtr.Zero)
                throw new InvalidOperationException("Failed to aggregate proofs");
            
            return new BatchProof(batchHandle);
        }
    }
}
