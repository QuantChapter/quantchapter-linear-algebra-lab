"""Exercise the public JSON boundary and atomic output behavior."""

from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest

from quantchapter_linear_algebra import cli

VALID = b'{"matrix":[[0,2],[1,3]],"rhs":[4,5]}\n'


@pytest.fixture
def source(tmp_path: Path) -> Path:
    path = tmp_path / "input.json"
    path.write_bytes(VALID)
    return path


def test_stdout_and_exact_input_digest(source: Path, capsys: pytest.CaptureFixture[str]) -> None:
    assert cli.main([str(source)]) == 0
    output = json.loads(capsys.readouterr().out)
    assert output["diagnostics"]["solution"] == pytest.approx([-1, 2], abs=1e-14)
    assert output["input_sha256"] == hashlib.sha256(VALID).hexdigest()
    assert output["residual_convention"] == "b - A*x"
    assert output["schema_version"] == 1


def test_output_replacement_and_failure_preserve_previous(source: Path, tmp_path: Path) -> None:
    destination = tmp_path / "reports" / "result.json"
    args = [str(source), "--output", str(destination)]
    assert cli.main(args) == 0
    original = destination.read_bytes()
    assert cli.main(args) == 2
    assert destination.read_bytes() == original
    destination.write_text("old", encoding="utf-8")
    assert cli.main([*args, "--force"]) == 0
    assert destination.read_bytes() == original
    source.write_text("invalid", encoding="utf-8")
    assert cli.main([*args, "--force"]) == 2
    assert destination.read_bytes() == original


def test_input_output_identity_and_force_without_output(source: Path) -> None:
    assert cli.main([str(source), "--force"]) == 2
    assert cli.main([str(source), "--output", str(source), "--force"]) == 2
    assert source.read_bytes() == VALID


@pytest.mark.parametrize(
    "content",
    [
        b"{",
        b"[]",
        b"null",
        b"{}",
        b'{"matrix":[],"rhs":[],"extra":0}',
        b'{"matrix":"1","rhs":[1]}',
        b'{"matrix":[[1]],"rhs":1}',
        b'{"matrix":[[1]],"rhs":[NaN]}',
        b'{"matrix":[[1]],"rhs":[Infinity]}',
        b'{"matrix":[[1]],"rhs":[1e999]}',
        b'{"matrix":[[true]],"rhs":[1]}',
        b'{"matrix":[[1]],"matrix":[[2]],"rhs":[1]}',
        b"\xff",
        b"[" * 2000 + b"]" * 2000,
    ],
)
def test_invalid_json_contract(
    source: Path, content: bytes, capsys: pytest.CaptureFixture[str]
) -> None:
    source.write_bytes(content)
    assert cli.main([str(source)]) == 2
    assert not capsys.readouterr().out


def test_missing_file_directory_and_byte_limit(
    source: Path, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    assert cli.main([str(tmp_path / "missing")]) == 2
    assert cli.main([str(tmp_path)]) == 2
    monkeypatch.setattr(cli, "MAX_BYTES", len(VALID) - 1)
    assert cli.main([str(source)]) == 2


def test_nonregular_opened_file_is_rejected(source: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    with monkeypatch.context() as patch:
        patch.setattr(os, "fstat", lambda _: SimpleNamespace(st_mode=0))
        with pytest.raises(ValueError, match="regular"):
            cli._snapshot(source)


def test_staging_failure_retains_old_output(
    source: Path, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    destination = tmp_path / "output.json"
    destination.write_text("old", encoding="utf-8")

    def fail(*args: object, **kwargs: object) -> None:
        raise OSError("simulated atomic replace failure")

    monkeypatch.setattr(os, "replace", fail)
    assert cli.main([str(source), "--output", str(destination), "--force"]) == 2
    assert destination.read_text(encoding="utf-8") == "old"
    assert sorted(path.name for path in tmp_path.iterdir()) == ["input.json", "output.json"]


def test_symlink_output_is_rejected(source: Path, tmp_path: Path) -> None:
    target, link = tmp_path / "target", tmp_path / "link"
    target.write_text("retained", encoding="utf-8")
    try:
        link.symlink_to(target)
    except OSError:
        pytest.skip("symlink creation is unavailable in this environment")
    assert cli.main([str(source), "--output", str(link), "--force"]) == 2
    assert target.read_text(encoding="utf-8") == "retained"


def test_module_entrypoint_and_version(source: Path) -> None:
    result = subprocess.run(
        [sys.executable, "-m", "quantchapter_linear_algebra", str(source)],
        capture_output=True,
        text=True,
        check=True,
    )
    assert json.loads(result.stdout)["diagnostics"]["row_swaps"] == 1
    with pytest.raises(SystemExit) as caught:
        cli.main(["--version"])
    assert caught.value.code == 0
