"""Bounded offline JSON input and atomic, versioned report output."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import stat
import sys
import tempfile
from collections.abc import Sequence
from dataclasses import asdict
from pathlib import Path
from typing import Any

from . import __version__, solve

MAX_BYTES = 20 * 1024 * 1024


def _unique_pairs(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for name, value in pairs:
        if name in result:
            raise ValueError(f"duplicate JSON key: {name}")
        result[name] = value
    return result


def _invalid_constant(value: str) -> None:
    raise ValueError(f"nonstandard JSON constant: {value}")


def _snapshot(path: Path) -> bytes:
    if not path.is_file():
        raise ValueError("input must be a regular JSON file")
    flags = os.O_RDONLY | getattr(os, "O_BINARY", 0) | getattr(os, "O_NONBLOCK", 0)
    descriptor = os.open(path, flags)
    with os.fdopen(descriptor, "rb") as stream:
        if not stat.S_ISREG(os.fstat(stream.fileno()).st_mode):
            raise ValueError("input must be a regular JSON file")
        content = stream.read(MAX_BYTES + 1)
    if len(content) > MAX_BYTES:
        raise ValueError("input exceeds the 20 MiB limit")
    return content


def _write(path: Path, content: str, *, force: bool) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.is_symlink():
        raise ValueError("output must not be a symbolic link")
    staged: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w", encoding="utf-8", newline="\n", dir=path.parent, delete=False
        ) as stream:
            staged = Path(stream.name)
            stream.write(content)
            stream.flush()
            os.fsync(stream.fileno())
        if force:
            os.replace(staged, path)
        else:
            os.link(staged, path)
    finally:
        if staged is not None:
            staged.unlink(missing_ok=True)


def main(argv: Sequence[str] | None = None) -> int:
    """Return 0 for success and 2 for invalid input or an output failure."""
    parser = argparse.ArgumentParser(description="Offline educational square-system solver.")
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    parser.add_argument("input", type=Path, help="UTF-8 JSON with exactly matrix and rhs keys")
    parser.add_argument("--rtol", type=float, default=1e-12)
    parser.add_argument("--output", type=Path, help="write JSON atomically; default is stdout")
    parser.add_argument("--force", action="store_true", help="replace existing output atomically")
    args = parser.parse_args(argv)
    try:
        if args.force and args.output is None:
            raise ValueError("--force requires --output")
        if args.output is not None and args.input.resolve() == args.output.resolve():
            raise ValueError("output must differ from input")
        content = _snapshot(args.input)
        payload = json.loads(
            content.decode("utf-8"),
            object_pairs_hook=_unique_pairs,
            parse_constant=_invalid_constant,
        )
        if not isinstance(payload, dict) or set(payload) != {"matrix", "rhs"}:
            raise ValueError("JSON must contain exactly matrix and rhs")
        if not isinstance(payload["matrix"], list) or not isinstance(payload["rhs"], list):
            raise ValueError("matrix and rhs must be JSON arrays")
        result = solve(payload["matrix"], payload["rhs"], rtol=args.rtol)
        report = {
            "schema_version": 1,
            "package_version": __version__,
            "input_sha256": hashlib.sha256(content).hexdigest(),
            "dimension": len(result.solution),
            "method": "Gaussian elimination with partial row pivoting",
            "residual_convention": "b - A*x",
            "diagnostics": asdict(result),
            "limitations": (
                "A small residual or backward error does not establish a small solution "
                "error for an ill-conditioned system. This is educational software."
            ),
        }
        encoded = json.dumps(report, indent=2, sort_keys=True, allow_nan=False) + "\n"
        if args.output is None:
            sys.stdout.write(encoded)
        else:
            _write(args.output, encoded, force=args.force)
    except (OSError, ValueError, RecursionError) as exc:
        print(f"quantchapter-linear-algebra: {exc}", file=sys.stderr)
        return 2
    return 0
