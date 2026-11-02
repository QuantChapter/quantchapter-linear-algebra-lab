# One point must satisfy both equations

You need basic arithmetic, substitution, and Python lists to follow this example.
A list such as `[0, 2]` stores the two coefficients of one equation. No matrix
calculus or prior numerical analysis is assumed. By the end, you should be able
to trace a row swap, check the resulting solution and explain what a residual can
and cannot tell you.

Suppose two conditions must hold at the same time:

$$
2y=4,
$$

$$
x+3y=5.
$$

The first condition gives $y=2$, because dividing both sides by 2 preserves the
equality. Substitution into the second gives $x+6=5$, so subtracting 6 from both
sides gives $x=-1$. This is one pair of values satisfying both conditions.

Writing the coefficients in an array gives the matrix equation $Ax=b$:

$$
A=\begin{pmatrix}0&2\\1&3\end{pmatrix},\qquad
\boldsymbol{x}=\begin{pmatrix}x\\y\end{pmatrix},\qquad
b=\begin{pmatrix}4\\5\end{pmatrix}.
$$

Here $A$ stores the coefficients row by row, the bold vector stores the unknown
values, and $b$ stores the right-hand sides in the same row order. The zero in
the first position means the first equation has no $x$ term. Multiplying each
row by the vector reproduces its equation.

## Why the first row must move

Elimination normally uses the first equation's coefficient of $x$ to remove
$x$ from the equations below it. That coefficient is called a **pivot**. In
our current first row it is zero. Dividing by it would be invalid.

Exchange the complete rows, including their right-hand sides:

$$
x+3y=5,\qquad 2y=4.
$$

We have not altered either condition. We have changed the order in which they
are processed. The first pivot is now 1. The second equation already has a zero
$x$ coefficient, so no subtraction is needed in this case.

Starting from the last equation gives $y=4/2=2$. Returning to the first gives
$x=(5-3\cdot2)/1=-1$. This process is **back substitution**: solve the last
remaining unknown first, then use it in earlier equations.

The package performs these operations while selecting the largest absolute
available pivot in each column. This is **partial row pivoting**. It avoids
choosing a needlessly small available coefficient; it does not eliminate every
source of numerical error.

```python
from quantchapter_linear_algebra import solve

result = solve([[0, 2], [1, 3]], [4, 5])
print(tuple(round(value, 8) for value in result.solution))
print(result.row_swaps)
```

The output is `(-1.0, 2.0)` and `1`. The unknowns retain their original column
order even though the equations changed row order during elimination.

## Check the original conditions

Substitute $x=-1$ and $y=2$ into the supplied equations, rather than checking only
the rearranged system:

$$
0(-1)+2(2)=4,\qquad 1(-1)+3(2)=5.
$$

Each calculated left-hand side matches the corresponding right-hand side. The
**residual** records the remaining difference, using the convention $r=b-Ax$.
Here both differences are zero, so `result.residual` is `(0.0, 0.0)`.

For contrast, consider the tempting wrong pair $(1,2)$. Its first condition still
works, because that equation ignores $x$. Its second left-hand side is $1+6=7$,
so its residual is $5-7=-2$. Checking only the first equation would have missed
the error. A solution must satisfy every original row.

The reported residual norm is the largest absolute component. For this wrong
pair the residual vector is $(0,-2)$ and its norm is 2. The norm is nonnegative
even though residual components can have either sign.

## Try a different elimination case

Consider $2x+y=5$ and $x-y=1$. Which pair satisfies both equations?

1. $(x,y)=(2,1)$
2. $(x,y)=(1,3)$
3. $(x,y)=(3,-1)$

The correct selection is **1**. To derive it, multiply the second equation by 2,
giving $2x-2y=2$. Subtract this from the first equation to remove $x$: $3y=3$,
so $y=1$. The second original equation then gives $x=2$. Substitution produces
$2(2)+1=5$ and $2-1=1$. Option 2 satisfies the first equation but gives $1-3=-2$
in the second. Option 3 satisfies the first but gives $3-(-1)=4$ in the second.
Again, one matching row is insufficient.

Run `solve([[2, 1], [1, -1]], [5, 1])` to compare the program's solution with this
independently worked result. This example needs elimination even though its first
pivot does not need a row swap.

## A small residual needs context

Floating-point arithmetic stores finitely many digits. The package normalizes
the system and rejects pivots too small relative to its coefficient scale.
This is a defensive rule, not a proof of mathematical singularity. A matrix can
be nonsingular and still have a pivot below the selected tolerance.

A second limitation concerns **conditioning**, meaning how strongly a solution
can change when its input changes slightly. Compare the first system below with
the system obtained by changing just its second right-hand side:

$$
x+y=2,\qquad x+1.000001y=2.000001,
$$

$$
x+y=2,\qquad x+1.000001y=2.000002.
$$

Subtract the first equation from the second. In the first system this gives
$0.000001y=0.000001$, so $(x,y)=(1,1)$. In the changed system it gives
$0.000001y=0.000002$, so $(x,y)=(0,2)$. A tiny input change caused a substantial
solution change. Each exact solution nevertheless has zero residual for its own
system. This is why a small residual does not establish that uncertain input
produced an accurate solution.

The backward-error diagnostic scales the residual by the sizes of the equation's
terms. It makes residuals easier to interpret across units. It does not measure
conditioning. The [numerical contract](api.md) gives the exact definition and
restrictions; the package does not provide a condition-number estimate.

When reviewing a result, check the original equations, the input units and
precision, the chosen tolerance, and whether input uncertainty could materially
change the conclusion. Software verification and learner understanding remain
separate forms of evidence.
