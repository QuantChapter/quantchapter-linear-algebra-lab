"""Execute the shipped row-swap example without third-party dependencies."""

from pathlib import Path

from quantchapter_linear_algebra.cli import main

if __name__ == "__main__":
    raise SystemExit(main([str(Path(__file__).resolve().parents[1] / "data/row_swap_system.json")]))
