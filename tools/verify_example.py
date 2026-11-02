"""Check the committed input and report against an independently known solution."""

from __future__ import annotations

import contextlib
import io
import json
import math
from pathlib import Path

from quantchapter_linear_algebra.cli import main

ROOT = Path(__file__).resolve().parents[1]


def verify() -> None:
    source = ROOT / "data/row_swap_system.json"
    if json.loads(source.read_text(encoding="utf-8")) != {
        "matrix": [[0, 2], [1, 3]],
        "rhs": [4, 5],
    }:
        raise ValueError("the teaching fixture no longer matches its worked comparison")
    stream = io.StringIO()
    with contextlib.redirect_stdout(stream):
        status = main([str(source)])
    if status:
        raise ValueError("the complete fixture command failed")
    report = json.loads(stream.getvalue())
    expected = json.loads((ROOT / "data/expected_report.json").read_text(encoding="utf-8"))
    if report != expected:
        raise ValueError("the saved report differs from the current executed result")
    diagnostics = report["diagnostics"]
    if not all(
        math.isclose(actual, target, abs_tol=1e-14)
        for actual, target in zip(diagnostics["solution"], [-1, 2], strict=True)
    ):
        raise ValueError("the computed solution disagrees with exact substitution")
    if diagnostics["row_swaps"] != 1 or diagnostics["residual"] != [0, 0]:
        raise ValueError("row swaps or original-system residual disagree with the worked case")
    print("Constructed input, exact worked solution and saved report agree.")


if __name__ == "__main__":
    verify()
