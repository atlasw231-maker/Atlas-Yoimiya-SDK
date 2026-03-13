import argparse
import platform
import sys
import threading
import time
from pathlib import Path


def _current_rss_bytes():
    system = platform.system()

    if system == "Windows":
        import ctypes
        from ctypes import wintypes

        class PROCESS_MEMORY_COUNTERS(ctypes.Structure):
            _fields_ = [
                ("cb", wintypes.DWORD),
                ("PageFaultCount", wintypes.DWORD),
                ("PeakWorkingSetSize", ctypes.c_size_t),
                ("WorkingSetSize", ctypes.c_size_t),
                ("QuotaPeakPagedPoolUsage", ctypes.c_size_t),
                ("QuotaPagedPoolUsage", ctypes.c_size_t),
                ("QuotaPeakNonPagedPoolUsage", ctypes.c_size_t),
                ("QuotaNonPagedPoolUsage", ctypes.c_size_t),
                ("PagefileUsage", ctypes.c_size_t),
                ("PeakPagefileUsage", ctypes.c_size_t),
            ]

        counters = PROCESS_MEMORY_COUNTERS()
        counters.cb = ctypes.sizeof(PROCESS_MEMORY_COUNTERS)
        kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
        psapi = ctypes.WinDLL("psapi", use_last_error=True)
        kernel32.GetCurrentProcess.restype = wintypes.HANDLE
        psapi.GetProcessMemoryInfo.argtypes = [
            wintypes.HANDLE,
            ctypes.POINTER(PROCESS_MEMORY_COUNTERS),
            wintypes.DWORD,
        ]
        psapi.GetProcessMemoryInfo.restype = wintypes.BOOL
        process = kernel32.GetCurrentProcess()
        ok = psapi.GetProcessMemoryInfo(process, ctypes.byref(counters), counters.cb)
        if ok:
            return int(counters.WorkingSetSize)
        return None

    proc_status = Path("/proc/self/status")
    if proc_status.exists():
        for line in proc_status.read_text().splitlines():
            if line.startswith("VmRSS:"):
                parts = line.split()
                if len(parts) >= 2:
                    return int(parts[1]) * 1024

    try:
        import resource

        rss = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
        if system == "Darwin":
            return int(rss)
        return int(rss) * 1024
    except Exception:
        return None


class PeakMemorySampler:
    def __init__(self, interval_seconds=0.01):
        self.interval_seconds = interval_seconds
        self._stop_event = threading.Event()
        self._thread = None
        self.max_rss_bytes = _current_rss_bytes()

    def start(self):
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()

    def stop(self):
        self._stop_event.set()
        if self._thread is not None:
            self._thread.join()
        current = _current_rss_bytes()
        if current is not None:
            if self.max_rss_bytes is None:
                self.max_rss_bytes = current
            else:
                self.max_rss_bytes = max(self.max_rss_bytes, current)
        return self.max_rss_bytes

    def _run(self):
        while not self._stop_event.wait(self.interval_seconds):
            current = _current_rss_bytes()
            if current is None:
                continue
            if self.max_rss_bytes is None:
                self.max_rss_bytes = current
            else:
                self.max_rss_bytes = max(self.max_rss_bytes, current)


def _format_mb(rss_bytes):
    if rss_bytes is None:
        return "N/A"
    return f"{rss_bytes / (1024 * 1024):.2f}"


def run_benchmark(constraint_sizes, warmup):
    bindings_path = Path(__file__).parent / "bindings" / "python"
    sys.path.insert(0, str(bindings_path))

    import yoimiya as y

    if warmup:
        warmup_constraints = constraint_sizes[0]
        y.prove_test_precompiled(warmup_constraints, [1] * (warmup_constraints + 1))

    print("constraints,prove_ms,verify_ms,proof_bytes,peak_rss_mb,valid")

    for num_constraints in constraint_sizes:
        witness = [1] * (num_constraints + 1)
        sampler = PeakMemorySampler()
        sampler.start()

        try:
            started = time.perf_counter()
            proof = y.prove_test_precompiled(num_constraints, witness)
            prove_ms = (time.perf_counter() - started) * 1000

            started = time.perf_counter()
            valid = proof.verify_precompiled()
            verify_ms = (time.perf_counter() - started) * 1000
            proof_bytes = proof.byte_size()
        finally:
            peak_rss = sampler.stop()

        peak_mb = _format_mb(peak_rss)

        print(f"{num_constraints},{prove_ms:.3f},{verify_ms:.3f},{proof_bytes},{peak_mb},{valid}")


def main():
    parser = argparse.ArgumentParser(
        description="Benchmark Yoimiya binary telemetry with prove/verify/proof-size/peak-memory output."
    )
    parser.add_argument(
        "--sizes",
        nargs="+",
        type=int,
        default=[100, 500, 1000, 2000, 10000, 50000, 100000, 250000, 500000, 1000000],
        help="Constraint sizes to benchmark.",
    )
    parser.add_argument(
        "--no-warmup",
        action="store_true",
        help="Disable the default precompiled SRS warmup run.",
    )
    args = parser.parse_args()
    run_benchmark(args.sizes, warmup=not args.no_warmup)


if __name__ == "__main__":
    main()