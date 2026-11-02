First public educational release of QuantChapter Linear Algebra Lab.

The dependency-free package solves finite square systems with partial row
pivoting and provides immutable solutions, original-system residual estimates,
relative backward errors and explicit numerical failure behavior. It includes a
bounded JSON CLI, a constructed row-swap fixture, a worked tutorial with complete
comparisons, and an optional intersection figure.

The release workflow verifies the Python/OS matrix, quality, dependency audit,
executed example, package metadata and isolated wheel installation before
publication. Attached wheel and source distributions have SHA-256 digests and
GitHub build-provenance attestations. Inspect the linked Actions runs for their
actual outcomes.

Residuals are computed in normalized floating-point arithmetic and rescaled.
A computed zero is not an exact certificate, and small backward error does not
establish small solution error for ill-conditioned input. Read the numerical
contract before relying on results outside the worked examples.

This pre-1.0 release is authored educational software; it does not establish
learner validation, production adoption or a numerical certification.
