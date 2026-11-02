"""Explain the shipped 2x2 system through its two intersecting lines."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

from quantchapter_linear_algebra import solve  # noqa: E402


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=Path("artifacts/row-swap-system.png"))
    parser.add_argument("--force", action="store_true", help="replace an existing figure")
    args = parser.parse_args()
    if args.output.is_symlink() or (args.output.exists() and not args.force):
        parser.error("output already exists or is a symlink; choose a different path")
    source = Path(__file__).resolve().parents[1] / "data/row_swap_system.json"
    if args.output.resolve() == source.resolve():
        parser.error("output must differ from the teaching input")
    payload = json.loads(source.read_text(encoding="utf-8"))
    result = solve(payload["matrix"], payload["rhs"])
    x_values = [-4 + index / 20 for index in range(161)]
    fig, axis = plt.subplots(figsize=(8, 5), layout="constrained")
    for index, (row, rhs) in enumerate(zip(payload["matrix"], payload["rhs"], strict=True)):
        y_values = [(rhs - row[0] * x) / row[1] for x in x_values]
        axis.plot(
            x_values,
            y_values,
            label=("2y = 4", "x + 3y = 5")[index],
            linestyle=("-", "--")[index],
            color=("#215b8f", "#873f31")[index],
            linewidth=2,
        )
    x, y = result.solution
    axis.scatter([x], [y], color="#222222", zorder=3)
    axis.annotate(f"Solution ({x:g}, {y:g})", (x, y), xytext=(12, 14), textcoords="offset points")
    axis.set(
        title="QuantChapter Linear Algebra Lab | One point satisfies both equations",
        xlabel="x (teaching units)",
        ylabel="y (teaching units)",
        xlim=(-4, 4),
        ylim=(-1, 5),
    )
    axis.set_aspect("equal", adjustable="box")
    axis.grid(color="#dedede", linewidth=0.7)
    axis.legend(loc="lower left")
    fig.supxlabel(
        "Constructed teaching example. Rows must swap before the first elimination pivot."
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(args.output, dpi=160, metadata={"Software": "QuantChapter Linear Algebra Lab"})
    plt.close(fig)
    print(f"Saved {args.output.name}; solution={result.solution}; residual={result.residual}")


if __name__ == "__main__":
    main()
