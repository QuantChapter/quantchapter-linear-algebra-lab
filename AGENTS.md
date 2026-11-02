# QuantChapter Linear Algebra Lab

Keep this independent public educational package focused on small, finite square
linear systems. Use Python 3.11–3.14 with no third-party runtime dependencies.

- Solve with partial-pivot Gaussian elimination; explain scale-aware pivot
  rejection and floating-point limits. Never imply that a small residual proves
  a small solution error for an ill-conditioned system.
- Preserve input values, typed immutable results, bounded JSON input and explicit
  validation errors. Keep file output atomic and prevent accidental overwrite.
- Check mathematics against independent Fraction calculations and mathematical
  properties. Keep examples deterministic and give every learner task a worked
  comparison. Authored examples are not learner validation.
- Run Ruff, strict mypy, branch-coverage tests, dependency audit, package metadata
  checks and a clean wheel install before release. Pin CI actions to verified SHAs.
- Do not commit environments, caches, credentials, personal data or local paths.
- Inspect the intended Git diff before committing. Do not modify other projects.
- Do not poll running work more frequently than once every five minutes; use
  blocking waits or completion events and pursue independent work meanwhile.
