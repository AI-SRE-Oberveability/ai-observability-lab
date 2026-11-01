# Local release candidate

[local-v0.1.0-source-candidate.json](local-v0.1.0-source-candidate.json) is a **source-pinned candidate**, not a deployable container release. It freezes four tested repository commits, their main CI receipts, the Docker base/Collector/Jaeger digest references already in reviewed source, and two native Windows package checksums. The workload image reference is deliberately null; no digest is inferred from a build-only image ID.

## Check the candidate

From the lab checkout:

```powershell
python scripts/validate_release.py
python scripts/validate_release.py --verify-sources
python -m unittest discover -s tests -v

# Expected exit 1 until image publication and replay are implemented/accepted:
python scripts/validate_release.py --require-deployable
```

The default checks are offline and structural. --verify-sources uses existing sibling Git clones: it binds the recorded CI receipt to each pinned commit/run, reads selected files from immutable Git objects, verifies their 18 hashes and compares image/native-package pins with those source files. It never fetches, checks out a different revision, publishes a package, starts services, calls Azure or changes credentials. It does not assert that the current working trees equal the release pins, independently attest CI, or prove that a registry artifact can be pulled.

The four repositories must be present and their pinned objects fetched by an operator before source verification. Public repositories can be cloned read-only without a shared admin/PAT credential. Current CI uses repository-scoped contents:read and no new coordination secret. Future private source access should use narrowly scoped read permissions; future image publication needs a separately reviewed job-scoped registry permission. Terraform OIDC/GitLab credentials do not serve as registry coordination credentials.

## What each pin means

- Repository commits are full immutable Git object IDs. Branches/tags are not release pins.
- Docker references include SHA256 digests. These may identify an index rather than a platform image; the selected platform/pull evidence still needs verification. The digest strings are copied from tested source, not newly resolved from a mutable tag.
- Native backend archives keep exact versions, HTTPS release URLs and SHA256 values. The existing native proof checked archives/executables, traces, privacy and lifecycle; that is separate from the unperformed container release replay.
- The lab execution pin names the already tested merged lab commit containing the proof runner. The new candidate manifest is identified by its own containing commit. This avoids a recursive self-pin.

## Remaining work before P2.4 is done

Select registry, image visibility and retention; review a concrete scoped publication workflow; publish and independently pull the workload image by digest; verify source/provenance and target platform; resolve/verify backend artifact availability; then replay the deterministic container cohort from the locked sources/images and record actual results. Keep mock and live-provider evidence separate. ACR creation/deployment remains behind the existing Azure gates. No registry publication, release tag or cloud resource is created by this candidate.

See [the release plan](../docs/release-pinning-plan.md), [main CI evidence](../evidence/main-ci-revalidation.json) and [HLD](../HLD.md).

References: [Docker digest concepts](https://docs.docker.com/dhi/explore/security-concepts/digests/) explain content references/indexes; [GitHub image publication](https://docs.github.com/en/actions/tutorials/publish-packages/publish-docker-images) is a reference for a future scoped workflow, not a configured publishing capability here.
