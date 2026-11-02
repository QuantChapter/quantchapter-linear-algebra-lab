"""Independent exact-rational checks, mathematical properties and failure cases."""

from __future__ import annotations

import math
from dataclasses import FrozenInstanceError
from fractions import Fraction
from itertools import repeat

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from quantchapter_linear_algebra import (
    MAX_DIMENSION,
    NumericalError,
    SingularMatrixError,
    solve,
)
from quantchapter_linear_algebra.solver import _dot


def rational_oracle(matrix: list[list[int]], rhs: list[int]) -> tuple[Fraction, ...]:
    """Exact Gauss-Jordan elimination; independent arithmetic and elimination form."""
    n = len(rhs)
    augmented = [
        [Fraction(value) for value in row] + [Fraction(rhs[i])] for i, row in enumerate(matrix)
    ]
    for column in range(n):
        pivot = next(row for row in range(column, n) if augmented[row][column])
        augmented[column], augmented[pivot] = augmented[pivot], augmented[column]
        divisor = augmented[column][column]
        augmented[column] = [value / divisor for value in augmented[column]]
        for row in range(n):
            if row == column:
                continue
            factor = augmented[row][column]
            augmented[row] = [
                value - factor * pivot_value
                for value, pivot_value in zip(augmented[row], augmented[column], strict=True)
            ]
    return tuple(row[-1] for row in augmented)


def test_row_swap_and_original_row_residual() -> None:
    result = solve([[0, 2], [1, 3]], [4, 5])
    assert result.solution == pytest.approx((-1.0, 2.0), abs=1e-14)
    assert result.residual == (0.0, 0.0)
    assert result.residual_norm == result.relative_backward_error == 0
    assert result.row_swaps == 1
    assert result.relative_pivot_tolerance == 1e-12


def test_known_elimination_case() -> None:
    result = solve([[2, 1], [1, -1]], [5, 1])
    assert result.solution == pytest.approx((2, 1))
    assert result.residual_norm < 1e-14


def test_zero_rhs_and_singleton() -> None:
    assert solve([[5]], [0]).solution == (0.0,)
    assert solve([[5]], [0]).relative_backward_error == 0
    assert solve([[2]], [7]).solution == (3.5,)


def test_accepts_iterators_and_preserves_inputs() -> None:
    matrix, rhs = [[3.0, 2.0], [1.0, 4.0]], [7.0, 9.0]
    original = [row.copy() for row in matrix]
    result = solve((iter(row) for row in matrix), iter(rhs))
    assert result.solution == pytest.approx((1, 2))
    assert matrix == original and rhs == [7.0, 9.0]
    with pytest.raises(FrozenInstanceError):
        result.row_swaps = 9  # type: ignore[misc]


@pytest.mark.parametrize("factor", [1e-150, -1e-100, 1e100, -1e150])
def test_global_scale_preserves_solution_and_pivot_decision(factor: float) -> None:
    result = solve([[0, 2 * factor], [factor, 3 * factor]], [4 * factor, 5 * factor])
    assert result.solution == pytest.approx((-1, 2), abs=1e-14)
    assert result.row_swaps == 1


def test_backward_error_avoids_overflowing_denominator() -> None:
    result = solve([[1, 1], [1, -1]], [1e308, 1e308])
    assert result.solution == (1e308, 0.0)
    assert result.relative_backward_error == 0


def test_fraction_numbers_are_supported() -> None:
    assert solve([[Fraction(2, 3)]], [Fraction(1, 3)]).solution == (0.5,)


def test_noninteger_scale_residual_agrees_with_exact_original_inputs_within_roundoff() -> None:
    matrix, rhs = [[0.3, 0.7], [0.2, 0.9]], [1.1, 0.4]
    result = solve(matrix, rhs)
    exact_residual = [
        float(
            Fraction(target)
            - sum(Fraction(a) * Fraction(x) for a, x in zip(row, result.solution, strict=True))
        )
        for row, target in zip(matrix, rhs, strict=True)
    ]
    equation_scale = max(sum(abs(a) for a in row) for row in matrix) * max(
        abs(x) for x in result.solution
    ) + max(abs(b) for b in rhs)
    # Compare with exact rational evaluation of the ORIGINAL stored floats,
    # allowing rounding from normalization, summation and physical rescaling.
    assert result.residual == pytest.approx(exact_residual, abs=16 * math.ulp(1.0) * equation_scale)


@pytest.mark.parametrize("unordered", [{1}, frozenset({1})])
def test_unordered_containers_are_not_interpreted_as_coordinate_order(unordered: object) -> None:
    with pytest.raises(ValueError):
        solve([[1]], unordered)  # type: ignore[arg-type]
    with pytest.raises(ValueError):
        solve(unordered, [1])  # type: ignore[arg-type]


@pytest.mark.parametrize(
    "matrix,rhs", [([[0]], [0]), ([[1, 2], [2, 4]], [3, 6]), ([[1, 2], [2, 4]], [3, 7])]
)
def test_singular_systems_do_not_claim_unique_solution(matrix: list, rhs: list) -> None:
    with pytest.raises(SingularMatrixError):
        solve(matrix, rhs)


def test_near_singularity_rejection_is_caller_controlled() -> None:
    matrix = [[1, 1], [1, 1.00000000000001]]
    rhs = [2, 2.00000000000001]
    with pytest.raises(SingularMatrixError, match="relative tolerance"):
        solve(matrix, rhs)
    relaxed = solve(matrix, rhs, rtol=0)
    assert relaxed.residual_norm < 1e-14


@pytest.mark.parametrize(
    "bad", [True, False, "1", None, 1j, math.inf, -math.inf, math.nan, 10**1000]
)
def test_invalid_coefficients_fail_explicitly(bad: object) -> None:
    with pytest.raises(ValueError):
        solve([[bad]], [1])  # type: ignore[list-item]
    with pytest.raises(ValueError):
        solve([[1]], [bad])  # type: ignore[list-item]


@pytest.mark.parametrize("bad", [-1, 1, 2, True, "0", math.nan, math.inf])
def test_tolerance_domain(bad: object) -> None:
    with pytest.raises(ValueError):
        solve([[1]], [1], rtol=bad)  # type: ignore[arg-type]


@pytest.mark.parametrize(
    "matrix", [[], [[]], [[1, 2]], [[1], [2]], "1", b"1", {}, None, [None], ["1"], [[1], [2, 3]]]
)
def test_invalid_matrix_shapes_and_containers(matrix: object) -> None:
    with pytest.raises(ValueError):
        solve(matrix, [1])  # type: ignore[arg-type]


@pytest.mark.parametrize("rhs", [[], [1, 2], None, "1", b"1", {}])
def test_rhs_shape_and_container(rhs: object) -> None:
    with pytest.raises(ValueError):
        solve([[1]], rhs)  # type: ignore[arg-type]


def test_bounded_iterables_reject_without_consuming_forever() -> None:
    with pytest.raises(ValueError, match="row limit"):
        solve(repeat([1]), [1])
    with pytest.raises(ValueError, match="value limit"):
        solve([repeat(1)], [1])
    with pytest.raises(ValueError, match="value limit"):
        solve([[1]], repeat(1))


def test_maximum_dimension_is_usable() -> None:
    matrix = [[float(i == j) for j in range(MAX_DIMENSION)] for i in range(MAX_DIMENSION)]
    result = solve(matrix, list(range(MAX_DIMENSION)))
    assert result.solution == tuple(range(MAX_DIMENSION))


@pytest.mark.parametrize(
    "matrix,rhs",
    [
        ([[1e-308]], [1e308]),
        ([[1e308]], [5e-324]),
        ([[1e308, 5e-324], [0, 1e308]], [1, 1]),
        ([[1, 1], [1, -1]], [1.7e308, -1.7e308]),
    ],
)
def test_unsafe_dynamic_range_is_rejected(matrix: list, rhs: list) -> None:
    with pytest.raises(NumericalError):
        solve(matrix, rhs)


def test_compensated_dot_and_summation_limits() -> None:
    assert _dot([1e16, 1, -1e16], [1, 1, 1]) == 1
    with pytest.raises(NumericalError):
        _dot([1.7e308, 1.7e308], [1, 1])
    with pytest.raises(NumericalError):
        _dot([1.7e308], [2])


@given(
    st.lists(st.lists(st.integers(-5, 5), min_size=3, max_size=3), min_size=3, max_size=3),
    st.lists(st.integers(-7, 7), min_size=3, max_size=3),
)
@settings(max_examples=100, deadline=None)
def test_against_exact_rational_oracle(matrix: list[list[int]], rhs: list[int]) -> None:
    # Strict row diagonal dominance supplies a nonsingular, bounded problem family.
    for index, row in enumerate(matrix):
        row[index] = sum(abs(value) for j, value in enumerate(row) if j != index) + 1
    expected = rational_oracle(matrix, rhs)
    result = solve(matrix, rhs)
    assert result.solution == pytest.approx(tuple(float(value) for value in expected), abs=1e-12)
    permuted = solve(matrix[::-1], rhs[::-1])
    assert permuted.solution == pytest.approx(result.solution, abs=1e-12)
    residual = [
        float(
            Fraction(target)
            - sum(Fraction(a) * Fraction(x) for a, x in zip(row, result.solution, strict=True))
        )
        for row, target in zip(matrix, rhs, strict=True)
    ]
    assert result.residual == pytest.approx(residual, abs=2e-14)
    denominator = max(sum(abs(a) for a in row) for row in matrix) * max(
        abs(x) for x in result.solution
    ) + max(abs(b) for b in rhs)
    reference_error = max(abs(r) for r in residual) / denominator if denominator else 0
    assert result.relative_backward_error == pytest.approx(reference_error, abs=2e-15)
