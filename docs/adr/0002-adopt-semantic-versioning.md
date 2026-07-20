# ADR-0002: Adopt Semantic Versioning

* **Status:** Accepted
* **Date:** 2026-07-20

## Context

Ohtli requires a clear and predictable versioning strategy to communicate compatibility, manage releases, and support future implementations.

Without a formal versioning policy, users and contributors cannot determine the impact of changes between releases.

## Decision

Ohtli adopts Semantic Versioning (SemVer).

Version numbers follow the format:

```
MAJOR.MINOR.PATCH
```

The versioning policy is defined in `docs/versioning/semantic-versioning.md`.

## Consequences

### Advantages

* Predictable release cycle.
* Clear compatibility guarantees.
* Well-established industry standard.
* Supports future tooling and automation.

### Trade-offs

* Contributors must correctly classify changes.
* Breaking changes require major version increments.

## Alternatives Considered

* Calendar Versioning (CalVer)
* Sequential version numbers
* Custom versioning schemes

Semantic Versioning was selected because it best communicates compatibility and project maturity.
