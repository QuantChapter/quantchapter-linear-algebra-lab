# Contributing

Keep changes focused on mathematical correctness, explicit numerical contracts,
readable teaching and reproducibility. Discuss additional algorithms before
implementation. Sparse, complex, rectangular and production service solvers are
outside this first release's scope.

Install Python 3.11–3.14 and [uv](https://docs.astral.sh/uv/getting-started/installation/).
From a cloned checkout:

```shell
uv sync --locked --all-extras --dev
uv run --frozen ruff check .
uv run --frozen ruff format --check .
uv run --frozen mypy
uv run --frozen pytest
uv run --frozen python tools/verify_example.py
uv run --frozen pip-audit --skip-editable
uv build --no-build-isolation
uv run --frozen python -m twine check --strict dist/*
uv run --frozen python tools/smoke_wheel.py
```

PowerShell does not expand wildcards for every native program; pass the wheel
and source archive filenames explicitly to Twine if `dist/*` is not expanded.
For a deliberate dependency change, update and review both `pyproject.toml` and
`uv.lock`. The lockfile captures the test, tooling, plotting and build dependency
resolution; ordinary checks must not rewrite it.

For a numerical change, provide an independently derived expected result,
appropriate tolerance, and a regression for the failure being fixed. Keep input
mutation, sign conventions, scaling and extreme values in review. Do not lower
the branch-coverage threshold to hide a gap. Document compatibility changes
and give every requested learner task a complete worked comparison.

Open a focused pull request explaining the concrete problem, resulting behavior,
checks actually run and remaining limitations. Keep private data, credentials,
local paths and fabricated performance claims out of code, examples and history.
Contributions must be your own work or clearly attributed compatible material,
and are provided under this repository's MIT license. Discuss the work respectfully.
Use [SECURITY.md](SECURITY.md) for private vulnerability reports.
