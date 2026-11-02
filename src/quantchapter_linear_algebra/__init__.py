"""Small, explicit linear-system calculations from QuantChapter."""

from .solver import MAX_DIMENSION, NumericalError, SingularMatrixError, Solution, solve

__version__ = "0.1.0"
__all__ = [
    "MAX_DIMENSION",
    "NumericalError",
    "SingularMatrixError",
    "Solution",
    "__version__",
    "solve",
]
