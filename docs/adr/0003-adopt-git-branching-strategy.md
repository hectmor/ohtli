# ADR-0003: Adopt Git Branching Strategy

* **Status:** Accepted
* **Date:** 2026-07-20

## Context

As Ohtli evolves beyond its initial specification, multiple features, documentation updates, and experiments will be developed in parallel.

A branching strategy is required to preserve stability while enabling continuous development.

## Decision

Ohtli adopts a lightweight branching model.

The primary branches are:

* `main`
* `develop`

Supporting branches include:

* `feature/*`
* `docs/*`
* `refactor/*`
* `experiment/*`
* `hotfix/*`

Development is integrated into `develop`.

Only stable releases are merged into `main`.

## Consequences

### Advantages

* Stable release history.
* Isolated feature development.
* Easier code review.
* Predictable release workflow.

### Trade-offs

* Slightly more Git overhead.
* Requires disciplined branch management.

## Alternatives Considered

* GitHub Flow
* Git Flow
* Trunk-Based Development

A lightweight branching strategy was selected because it balances simplicity with long-term maintainability.
