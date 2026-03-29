#!/usr/bin/env python3
"""
Yoimiya Benchmark Visualizer

Reads CSV output from benchmark_telemetry.py and produces performance charts:
  - Prove time (ms) vs. constraint count
  - Verify time (ms) vs. constraint count
  - Proof size (bytes) vs. constraint count
  - Peak memory (MB) vs. constraint count

Usage:
  # Capture benchmark data then visualize:
  python benchmark_telemetry.py --sizes 100 500 1000 2000 10000 > results.csv
  python visualize_benchmark.py results.csv

  # Pipe directly:
  python benchmark_telemetry.py | python visualize_benchmark.py -

  # Save charts to a specific directory:
  python visualize_benchmark.py results.csv --output-dir ./charts
"""

import argparse
import csv
import sys
from pathlib import Path


def _parse_csv(source):
    """Parse benchmark CSV rows, skipping comment/header lines."""
    rows = []
    reader = csv.DictReader(source)
    for row in reader:
        try:
            constraints = int(row["constraints"])
            prove_ms = float(row["prove_ms"])
            verify_ms = float(row["verify_ms"])
            proof_bytes = int(row["proof_bytes"])
            peak_rss_mb_raw = row["peak_rss_mb"]
            peak_rss_mb = float(peak_rss_mb_raw) if peak_rss_mb_raw not in ("N/A", "") else None
            valid = row["valid"].strip().lower() in ("true", "1", "yes")
            rows.append(
                {
                    "constraints": constraints,
                    "prove_ms": prove_ms,
                    "verify_ms": verify_ms,
                    "proof_bytes": proof_bytes,
                    "peak_rss_mb": peak_rss_mb,
                    "valid": valid,
                }
            )
        except (KeyError, ValueError):
            continue
    return rows


def _plot(rows, output_dir):
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except ImportError:
        print(
            "matplotlib is required for plotting. Install with: pip install matplotlib",
            file=sys.stderr,
        )
        sys.exit(1)

    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    xs = [r["constraints"] for r in rows]

    charts = [
        ("prove_ms", "Prove time (ms)", "Prove Time vs. Constraints", "prove_time.png"),
        ("verify_ms", "Verify time (ms)", "Verify Time vs. Constraints", "verify_time.png"),
        ("proof_bytes", "Proof size (bytes)", "Proof Size vs. Constraints", "proof_size.png"),
    ]

    for key, ylabel, title, filename in charts:
        ys = [r[key] for r in rows]
        fig, ax = plt.subplots(figsize=(8, 5))
        ax.plot(xs, ys, marker="o", linewidth=2)
        ax.set_xlabel("Constraint count")
        ax.set_ylabel(ylabel)
        ax.set_title(title)
        ax.grid(True, linestyle="--", alpha=0.5)
        ax.set_xscale("log")
        path = output_dir / filename
        fig.tight_layout()
        fig.savefig(path, dpi=150)
        plt.close(fig)
        print(f"  Saved: {path}")

    # Memory chart — skip rows where memory could not be sampled
    mem_rows = [r for r in rows if r["peak_rss_mb"] is not None]
    if mem_rows:
        xs_mem = [r["constraints"] for r in mem_rows]
        ys_mem = [r["peak_rss_mb"] for r in mem_rows]
        fig, ax = plt.subplots(figsize=(8, 5))
        ax.plot(xs_mem, ys_mem, marker="o", color="tab:orange", linewidth=2)
        ax.set_xlabel("Constraint count")
        ax.set_ylabel("Peak RSS (MB)")
        ax.set_title("Peak Memory vs. Constraints")
        ax.grid(True, linestyle="--", alpha=0.5)
        ax.set_xscale("log")
        path = output_dir / "peak_memory.png"
        fig.tight_layout()
        fig.savefig(path, dpi=150)
        plt.close(fig)
        print(f"  Saved: {path}")

    # Summary chart: prove + verify on the same axes
    ys_prove = [r["prove_ms"] for r in rows]
    ys_verify = [r["verify_ms"] for r in rows]
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.plot(xs, ys_prove, marker="o", label="Prove", linewidth=2)
    ax.plot(xs, ys_verify, marker="s", label="Verify", linewidth=2)
    ax.set_xlabel("Constraint count")
    ax.set_ylabel("Time (ms)")
    ax.set_title("Prove & Verify Time vs. Constraints")
    ax.legend()
    ax.grid(True, linestyle="--", alpha=0.5)
    ax.set_xscale("log")
    path = output_dir / "summary.png"
    fig.tight_layout()
    fig.savefig(path, dpi=150)
    plt.close(fig)
    print(f"  Saved: {path}")


def _print_table(rows):
    """Print a simple ASCII summary table."""
    header = f"{'Constraints':>12}  {'Prove (ms)':>10}  {'Verify (ms)':>11}  {'Bytes':>8}  {'RSS (MB)':>9}  {'Valid':>5}"
    print(header)
    print("-" * len(header))
    for r in rows:
        rss = f"{r['peak_rss_mb']:.2f}" if r["peak_rss_mb"] is not None else "N/A"
        print(
            f"{r['constraints']:>12}  {r['prove_ms']:>10.3f}  {r['verify_ms']:>11.3f}"
            f"  {r['proof_bytes']:>8}  {rss:>9}  {'✓' if r['valid'] else '✗':>5}"
        )


def main():
    parser = argparse.ArgumentParser(
        description="Visualize Yoimiya benchmark telemetry as performance charts."
    )
    parser.add_argument(
        "input",
        nargs="?",
        default="-",
        help="CSV file produced by benchmark_telemetry.py, or '-' to read from stdin (default: -).",
    )
    parser.add_argument(
        "--output-dir",
        default="benchmark_charts",
        help="Directory to write PNG charts into (default: benchmark_charts).",
    )
    parser.add_argument(
        "--no-plot",
        action="store_true",
        help="Print summary table only; do not generate chart images.",
    )
    args = parser.parse_args()

    if args.input == "-":
        source = sys.stdin
    else:
        path = Path(args.input)
        if not path.exists():
            print(f"Error: file not found: {path}", file=sys.stderr)
            sys.exit(1)
        source = path.open()

    try:
        rows = _parse_csv(source)
    finally:
        if args.input != "-":
            source.close()

    if not rows:
        print("No valid benchmark rows found in input.", file=sys.stderr)
        sys.exit(1)

    print(f"\nLoaded {len(rows)} benchmark rows.\n")
    _print_table(rows)

    if not args.no_plot:
        print(f"\nGenerating charts in '{args.output_dir}/'...")
        _plot(rows, args.output_dir)
        print("\nDone.")


if __name__ == "__main__":
    main()
