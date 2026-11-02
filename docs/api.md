# API and numerical conventions

```python
from quantchapter_linear_algebra import solve, SingularMatrixError, NumericalError

result = solve([[0, 2], [1, 3]], [4, 5], rtol=1e-12)
```

`solve(matrix, rhs, *, rtol=1e-12)` consumes ordered iterables, validates them,
and copies their finite values into independent tuples. Neither argument is
mutated. The matrix must have 1–256 rows, each with exactly that many entries.
The right-hand side must have the same length. Numeric inputs must implement
Python's real-number interface and be representable as finite floats; integers
and floats are supported. Strings, booleans and nonfinite numbers are rejected.
There is no complex, rectangular, sparse or least-squares solver in this release.

## Result

The frozen `Solution` dataclass contains:

| Field | Meaning |
| --- | --- |
| `solution` | Tuple of solution components in the original column order |
| `residual` | Tuple representing `b - A*x`, in the original row order and units |
| `residual_norm` | Infinity norm: largest absolute residual component |
| `relative_backward_error` | Dimensionless residual divided by `||A||∞||x||∞ + ||b||∞` |
| `row_swaps` | Number of elimination row exchanges |
| `relative_pivot_tolerance` | The validated caller-supplied tolerance |

`||v||∞` means the largest absolute component of a vector. For a matrix it
means the largest row sum of absolute coefficients. With a zero right-hand
side, the zero solution has zero residual and a defined reported backward error
of zero, including the zero-over-zero denominator case for this result.

## Pivot rejection and scaling

Let `s` be the largest absolute matrix coefficient. The solver divides both
`A` and `b` by `s` before elimination, preserving the represented equations.
At each column, it exchanges the current row with a row containing the largest
absolute remaining coefficient in that column. It rejects a computed pivot `p`
when `abs(p) <= rtol` in this normalized system. Equivalently, the threshold
uses the original coefficient scale, including subsequent elimination growth.

`rtol` must be a finite real number in `[0, 1)`. The default `1e-12` is a
conservative educational rejection rule, not a universal accuracy guarantee.
It may reject a mathematically nonsingular but poorly scaled or nearly singular
system. A zero tolerance rejects only computed zero pivots, but cannot restore
information already lost to floating-point rounding. Global rescaling by a
representable nonzero factor preserves the intended pivot test; row-by-row
rescaling changes the matrix's numerical conditioning and may change rejection.

## Residual and backward error

After back substitution, diagnostics use the original, unpermuted system.
Products are accumulated with `math.fsum` in the normalized equations and the
residual is converted back to original units. The backward-error denominator
is evaluated in scaled form to avoid unnecessary overflow. These are
floating-point diagnostics, not exact-rational certificates. Normalization and
rescaling introduce their own rounding, so the reported residual can differ
from evaluating `b - A*x` directly in the original arithmetic. A computed zero
can conceal a nonzero exact-rational residual for the stored float values.

The quantity measures the residual relative to the size of the equation's terms.
It does not estimate the condition number. An ill-conditioned matrix can have
two very different solution vectors that produce very similar right-hand sides.
Consequently a small residual alone cannot establish a small solution error.
The independent rational oracle in tests verifies bounded constructed examples;
it does not extend a guarantee to all real inputs.

## Errors and numerical limits

- `ValueError`: malformed input, invalid dimensions, tolerance or numeric domain.
- `SingularMatrixError`, a `ValueError` subclass: a zero or rejected pivot, including
  singular, inconsistent, nonunique and some nearly singular systems. The solver
  does not attempt to distinguish every mathematical singular-system category.
- `NumericalError`, also a `ValueError` subclass: normalization underflow, overflow,
  a nonfinite intermediate, or an unrepresentable residual. Extreme dynamic-range
  systems may be rejected even if another algorithm could produce a finite answer.

Floating-point underflow or rounding can erase changes smaller than the available
precision. Only detected unsafe cases are rejected; there is no claim to detect
every accuracy loss. The algorithm uses cubic arithmetic work and quadratic memory.
The dimension cap bounds work but is not a performance or latency guarantee.

## JSON and output

The CLI reads one bounded snapshot of a regular file. It accepts UTF-8 JSON
with exactly `matrix` and `rhs` array keys; duplicate keys, `NaN`, `Infinity`,
nonfinite numeric literals and malformed JSON fail. Whitespace is allowed but
the input digest always refers to the exact original bytes. Matrix row lengths
and numeric contents are checked by the shared solver. No network access occurs.

The CLI returns 0 on success and 2 for normal validation or filesystem errors.
Without `--output`, JSON goes to stdout. A report file is staged in its destination
directory, flushed and published atomically. The default publication refuses an
existing destination, including races; `--force` permits atomic replacement.
An existing final-path symlink and an input/output path identity are rejected.
Filesystems that cannot support the required link or replace operation report an
error; the command does not silently fall back to a potentially partial write.
Filesystem atomicity is not a promise of durability after arbitrary power loss.
