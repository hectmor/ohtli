# Architecture Decision Records

This directory contains the Architecture Decision Records (ADRs) for the Ohtli project.

## Purpose

ADRs document significant architectural decisions made during the development of Ohtli. They explain the context, the decision, the alternatives considered, and the consequences.

Their goal is to preserve the reasoning behind important design choices and provide historical traceability as the framework evolves.

## Naming Convention

Each ADR follows the format:

```text
NNNN-title.md
```

Examples:

* `0001-adopt-architecture-decision-records.md`
* `0002-adopt-markdown-first.md`
* `0003-use-kebab-case.md`

Numbers are sequential and are never reused.

## ADR Template

Each ADR should contain the following sections:

* Title
* Status
* Date
* Context
* Decision
* Alternatives Considered
* Consequences
* Related Decisions

## Status Values

* Proposed
* Accepted
* Superseded
* Deprecated

## Guidelines

* One architectural decision per ADR.
* ADRs record decisions, not implementation details.
* Once accepted, ADRs should not be modified except for minor corrections.
* If a decision changes, create a new ADR that supersedes the previous one.
