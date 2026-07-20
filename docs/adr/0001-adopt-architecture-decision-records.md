# ADR-0001: Adopt Architecture Decision Records

## Status

Accepted

## Date

2026-07-20

## Context

Ohtli is intended to be a long-lived framework. As the project evolves, architectural decisions need to remain understandable and traceable. Relying solely on Git history or discussions makes it difficult to understand why a decision was made.

## Decision

Adopt Architecture Decision Records (ADRs) as the official mechanism for documenting significant architectural decisions.

Each important architectural decision will be recorded as a separate ADR using sequential numbering.

## Alternatives Considered

### Rely on Git history

Rejected because commit messages do not provide sufficient context or rationale.

### Document decisions in architecture documents

Rejected because architectural documents describe the current design, not the decision-making process.

## Consequences

### Positive

* Architectural decisions become traceable.
* Design rationale is preserved.
* Future contributors can understand the evolution of the framework.
* Changes can be managed through superseding ADRs.

### Negative

* Requires maintaining an additional document for significant decisions.
* Introduces a small amount of documentation overhead.

## Related Decisions

None.
