from __future__ import annotations

import argparse
from pathlib import Path

from .plots import plot_detection_comparison, plot_precision_recall, plot_timing_comparison


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate comparison plots from model result JSON files.")
    parser.add_argument("results", type=Path, help="Detection result JSON file or directory")
    parser.add_argument("--timing-results", type=Path, help="Timing result JSON file or directory")
    parser.add_argument("--output-dir", type=Path, default=Path("evaluation/plots"))
    args = parser.parse_args()
    plot_detection_comparison(args.results, args.output_dir / "detection_comparison.png")
    plot_precision_recall(args.results, args.output_dir / "precision_recall.png")
    if args.timing_results:
        plot_timing_comparison(args.timing_results, args.output_dir / "timing_comparison.png")


if __name__ == "__main__":
    main()
