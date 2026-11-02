"""Partial-pivot Gaussian elimination with explicit floating-point diagnostics."""

from __future__ import annotations

import math
from collections.abc import Iterable
from dataclasses import dataclass
from numbers import Real

MAX_DIMENSION = 256


class SingularMatrixError(ValueError):
    """A pivot is zero or below the caller's relative rejection tolerance."""


class NumericalError(ValueError):
    """A required intermediate or diagnostic cannot be represented safely."""


@dataclass(frozen=True)
class Solution:
    """Immutable solution and diagnostics for the ORIGINAL supplied system.

    residual estimates b - A*x by computing in globally normalized arithmetic
    and then rescaling. It may differ from direct original-scale evaluation.
    The backward error describes this computed residual; neither a small value
    nor a computed zero certifies an exact solution or bounds forward error.
    """

    solution: tuple[float, ...]
    residual: tuple[float, ...]
    residual_norm: float
    relative_backward_error: float
    row_swaps: int
    relative_pivot_tolerance: float


def _number(value: object, name: str) -> float:
    if isinstance(value, bool) or not isinstance(value, Real):
        raise ValueError(f"{name} must contain real numbers, excluding booleans")
    try:
        result = float(value)
    except (ValueError, OverflowError) as exc:
        raise ValueError(f"{name} must be representable as finite floats") from exc
    if not math.isfinite(result):
        raise ValueError(f"{name} must contain finite numbers")
    return result


def _vector(values: Iterable[float], name: str) -> tuple[float, ...]:
    if isinstance(values, (str, bytes, dict, set, frozenset)):
        raise ValueError(f"{name} must be an ordered iterable of real numbers")
    result: list[float] = []
    try:
        for value in values:
            if len(result) == MAX_DIMENSION:
                raise ValueError(f"{name} exceeds the {MAX_DIMENSION}-value limit")
            result.append(_number(value, name))
    except TypeError as exc:
        raise ValueError(f"{name} must be an ordered iterable of real numbers") from exc
    return tuple(result)


def _matrix(values: Iterable[Iterable[float]]) -> tuple[tuple[float, ...], ...]:
    if isinstance(values, (str, bytes, dict, set, frozenset)):
        raise ValueError("matrix must contain ordered rows")
    rows: list[tuple[float, ...]] = []
    try:
        for row in values:
            if len(rows) == MAX_DIMENSION:
                raise ValueError(f"matrix exceeds the {MAX_DIMENSION}-row limit")
            rows.append(_vector(row, "matrix row"))
    except TypeError as exc:
        raise ValueError("matrix must contain ordered rows") from exc
    if not rows or any(len(row) != len(rows) for row in rows):
        raise ValueError("matrix must be nonempty and square")
    return tuple(rows)


def _finite(value: float) -> float:
    if not math.isfinite(value):
        raise NumericalError("a calculation exceeded finite floating-point range")
    return value


def _dot(left: Iterable[float], right: Iterable[float]) -> float:
    try:
        return _finite(math.fsum(_finite(a * b) for a, b in zip(left, right, strict=True)))
    except OverflowError as exc:
        raise NumericalError("a summation exceeded finite floating-point range") from exc


def solve(
    matrix: Iterable[Iterable[float]], rhs: Iterable[float], *, rtol: float = 1e-12
) -> Solution:
    """Solve a finite square A*x=b using partial-pivot Gaussian elimination.

    Inputs are copied and never mutated. Dimensions are bounded to 1..256.
    Global normalization divides A and b by max(abs(A)); a pivot whose normalized
    magnitude is <= rtol is rejected. rtol must be finite and in [0, 1).
    Default rejection is deliberately conservative and is not a condition-number
    estimate. rtol=0 rejects only computed zero pivots, without guaranteeing an
    accurate result. Nonfinite/underflowed normalization and unsafe intermediates
    raise NumericalError. No least-squares or singular-system solution is implied.
    """
    original = _matrix(matrix)
    target = _vector(rhs, "rhs")
    n = len(original)
    if len(target) != n:
        raise ValueError("rhs length must match the matrix dimension")
    tolerance = _number(rtol, "rtol")
    if not 0 <= tolerance < 1:
        raise ValueError("rtol must lie in [0, 1)")
    scale = max(abs(value) for row in original for value in row)
    if scale == 0:
        raise SingularMatrixError("matrix is zero; no unique solution is available")
    normalized = tuple(tuple(value / scale for value in row) for row in original)
    normalized_rhs = tuple(_finite(value / scale) for value in target)
    if any(
        value != 0 and normalized[i][j] == 0
        for i, row in enumerate(original)
        for j, value in enumerate(row)
    ) or any(value != 0 and normalized_rhs[i] == 0 for i, value in enumerate(target)):
        raise NumericalError("normalization underflowed; rescale the supplied system")
    work = [list(row) for row in normalized]
    transformed_rhs = list(normalized_rhs)
    swaps = 0
    for column in range(n):
        pivot_row = max(range(column, n), key=lambda row: abs(work[row][column]))
        if abs(work[pivot_row][column]) <= tolerance:
            raise SingularMatrixError(
                f"pivot {column + 1} is zero or below the relative tolerance; "
                "a unique accurate solution is not established"
            )
        if pivot_row != column:
            work[column], work[pivot_row] = work[pivot_row], work[column]
            transformed_rhs[column], transformed_rhs[pivot_row] = (
                transformed_rhs[pivot_row],
                transformed_rhs[column],
            )
            swaps += 1
        for row in range(column + 1, n):
            factor = work[row][column] / work[column][column]
            work[row][column] = 0.0
            for index in range(column + 1, n):
                work[row][index] = _finite(work[row][index] - factor * work[column][index])
            transformed_rhs[row] = _finite(transformed_rhs[row] - factor * transformed_rhs[column])
    values = [0.0] * n
    for row in range(n - 1, -1, -1):
        remainder = _dot(work[row][row + 1 :], values[row + 1 :])
        numerator = _finite(transformed_rhs[row] - remainder)
        values[row] = _finite(numerator / work[row][row])
    scaled_residual = tuple(
        _finite(target_value - _dot(row, values))
        for row, target_value in zip(normalized, normalized_rhs, strict=True)
    )
    residual = tuple(_finite(value * scale) for value in scaled_residual)
    matrix_norm = max(math.fsum(abs(value) for value in row) for row in normalized)
    x_norm = max(abs(value) for value in values)
    b_norm = max(abs(value) for value in normalized_rhs)
    denominator_scale = max(x_norm, b_norm)
    if denominator_scale == 0:
        backward_error = 0.0
    else:
        denominator = matrix_norm * (x_norm / denominator_scale) + b_norm / denominator_scale
        backward_error = max(abs(value) for value in scaled_residual) / denominator_scale
        backward_error /= denominator
    return Solution(
        solution=tuple(values),
        residual=residual,
        residual_norm=max(abs(value) for value in residual),
        relative_backward_error=backward_error,
        row_swaps=swaps,
        relative_pivot_tolerance=tolerance,
    )
