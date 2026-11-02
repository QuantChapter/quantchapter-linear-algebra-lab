# Release process

The gate below defines required work. Actual test results and GitHub Actions runs
provide evidence; this document is not proof that an unrun check has passed.

1. Inspect the complete Git diff and exclude private material, machine paths,
   credentials and unrelated changes. Review numerical behavior independently.
2. Update the manifest/package version, changelog, release notes and lockfile
   deliberately. Run the checks in [CONTRIBUTING.md](../CONTRIBUTING.md).
3. Confirm the tutorial, fixture, saved report and figure agree with execution.
   Review a changed calculation using exact-rational or independently derived
   references and state its assumptions and limits.
4. Build the wheel and source archive using the locked Hatchling backend,
   validate their metadata, and install the wheel without dependencies in a
   clean environment outside the source checkout.
5. Merge reviewed work into `main`, confirm the remote Python/OS matrix, quality,
   example, package and CodeQL checks, then create a new version tag.
6. Inspect the release's tag, artifacts, SHA-256 digests, build-provenance
   attestations and linked workflow results after publication.

The configured matrix covers Python 3.11 and 3.14 on Linux, Windows and macOS,
plus Python 3.12 and 3.13 on Linux. Ordinary workflows have read-only tokens and
SHA-pinned actions. The release workflow reuses CI, checks tag/main ancestry and
version agreement, then publishes a GitHub release with wheel, source archive,
checksums and provenance. No workflow publishes to PyPI.

Use the actual next version in place of `v0.1.0`:

```shell
git tag -a v0.1.0 -m "QuantChapter Linear Algebra Lab 0.1.0"
git push origin v0.1.0
```

Do not move a published tag. A correction requires a new version and changelog
entry. Build provenance identifies source and workflow, without proving accuracy
or suitability. Consumers can compare the attached SHA-256 digests and verify a
downloaded wheel's provenance with:

```shell
gh attestation verify PATH_TO_WHEEL --repo QuantChapter/quantchapter-linear-algebra-lab
```

Remote settings must be inspected independently: keep the repository public,
protect `main` with the successful checks, disable force pushes and deletion,
enable dependency alerts/secret scanning/push protection/private reporting where
available, and restrict collaborator permissions. Once a second human maintainer
is available, require independent pull-request approval and code-owner review.
A sole maintainer cannot independently approve their own pull request.

Dependencies are reviewed through weekly Dependabot pull requests. Confirm the
advisory service actually ran before reporting a clean audit; do not suppress an
advisory simply to obtain a passing check. Reassess metadata and supported Python
versions when a secure dependency floor changes.

References: [uv locking](https://docs.astral.sh/uv/concepts/projects/sync/),
[GitHub repository practices](https://docs.github.com/en/repositories/creating-and-managing-repositories/best-practices-for-repositories),
and [build-provenance attestations](https://docs.github.com/en/actions/how-tos/secure-your-work/use-artifact-attestations/use-artifact-attestations).
