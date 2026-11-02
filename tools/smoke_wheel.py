"""Install the built wheel without dependencies and execute it outside the checkout."""

from __future__ import annotations

import json
import os
import subprocess
import tempfile
import venv
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    wheels = list((ROOT / "dist").glob("*.whl"))
    if len(wheels) != 1:
        raise ValueError("expected exactly one built wheel")
    with tempfile.TemporaryDirectory() as directory:
        work = Path(directory)
        environment = work / "venv"
        venv.EnvBuilder(with_pip=True).create(environment)
        scripts = environment / ("Scripts" if os.name == "nt" else "bin")
        python = scripts / ("python.exe" if os.name == "nt" else "python")
        command = scripts / (
            "quantchapter-linear-algebra.exe" if os.name == "nt" else "quantchapter-linear-algebra"
        )
        subprocess.run(
            [str(python), "-I", "-m", "pip", "install", "--no-deps", str(wheels[0])],
            cwd=work,
            check=True,
        )
        subprocess.run(
            [
                str(python),
                "-I",
                "-c",
                "import math; from quantchapter_linear_algebra import solve; "
                "r = solve([[0, 2], [1, 3]], [4, 5]); "
                "assert math.isclose(r.solution[0], -1, abs_tol=1e-14); "
                "assert r.row_swaps == 1; assert r.residual == (0, 0)",
            ],
            cwd=work,
            check=True,
        )
        source = work / "system.json"
        source.write_bytes((ROOT / "data/row_swap_system.json").read_bytes())
        output = work / "report.json"
        subprocess.run([str(command), "--version"], cwd=work, check=True)
        subprocess.run([str(command), str(source), "--output", str(output)], cwd=work, check=True)
        report = json.loads(output.read_text(encoding="utf-8"))
        if report != json.loads((ROOT / "data/expected_report.json").read_text(encoding="utf-8")):
            raise ValueError("installed wheel report differs from the reviewed example")
    print("Isolated wheel API, entry point and full report passed outside the checkout.")


if __name__ == "__main__":
    main()
