# Implementation Boundaries

## Status

Defined

## Purpose

This document defines the minimal seams that the canonical architecture
already forces on any real implementation, independent of technology.

It does not design an implementation. It states where implementation
concerns must not cross into architectural concerns, and vice versa.

```text
Canonical Models: What is true regardless of technology?
Implementation Boundaries: What seams do those models force on real code?
An Implementation: A concrete technology choice that respects those seams.
```

## Scope

This document covers only the boundaries the existing canonical models
(`domain-model/`, `interaction-model/`, `event-model/`, `workflow-model/`,
`representation-model/`, `execution-model/`, `user-experience/`,
`automation-model/`, `filesystem-model/`, `metadata-model/`) already
require. It does not define testing strategy, error or failure
handling, configuration management, or runtime composition /
dependency injection. Those require a real vertical slice to evaluate
against and are deliberately deferred.

## Required Seams

Each canonical model implies a corresponding implementation concern that
must remain separable from the others:

| Canonical Model | Implementation Concern |
| --- | --- |
| Domain Model | Domain Objects and their identity, independent of storage or display |
| Interaction Model | Relationships between Domain Objects |
| Event Model | Historical evidence of observable change |
| Workflow Model | Transformations available to relevant state |
| Representation Model | Canonical representation, independent of physical medium |
| Execution Model | What it means for a Workflow to happen, independent of who or what triggers it |
| Filesystem Model | Physical organization of a representation on disk |
| Metadata Model | Structured description of a representation |
| Automation Model | Actor-neutral initiation of a Workflow Execution |

No implementation concern may absorb another. In particular:

```text
Domain logic     != Representation logic
Representation   != Filesystem organization
Filesystem I/O   != Workflow logic
Workflow logic   != Execution trigger (Human, Deterministic, AI-Assisted, Hybrid)
```

## Technology Independence

Choosing an implementation language or a target platform selects *an*
implementation. It does not alter, extend, or restrict any canonical
model.

```text
Python (language choice)   != Architecture
Obsidian (platform choice) != Architecture
```

See ADR-0005 for the specific decision to use Python and Obsidian, and
for what that decision explicitly does not change.

## Reconciling Existing Implementations

Two directories in this repository already function as de facto
implementations and predate the canonical Domain Model:
`implementations/reference/` and `implementations/platforms/obsidian/vault/`.

Both contain `inbox/` and `reviews/` top-level folders. Neither folder's
content asserts that Inbox or Review are Domain Objects — they describe
functional staging areas, not entities with identity. Per the
Filesystem Model, directory naming carries no semantic authority
(`Directory structure != Domain semantics`), so these folders are
retained as implementation-level conveniences rather than renamed:

- `inbox/` is the physical staging area for the Workflow Model's
  Capture transformation class (informational). It is not a Domain
  Object.
- `reviews/` is the physical storage location for outputs of the
  Workflow Model's Review transformation class (evaluative). It is not
  a Domain Object.

`templates/` (Automation Model), `knowledge/` (grouping the Reference
and Resource Domain Objects), `archive/` (physical location associated
with the Workflow Model's Archive transformation), and `attachments/`
(non-Markdown resources associated with a Domain Object) are retained
under the same reasoning: their names describe implementation-level
organization, not domain semantics.

`vault/templates/` already implements the Domain Model's Core Objects
(Project, Area, Meeting, Reference, Resource, Journal Entry) and
requires no change.

## Architectural Boundaries

This document does not define a package structure, module layout,
class hierarchy, testing approach, error handling strategy,
configuration format, or dependency injection mechanism. Those are
implementation-architecture decisions to be made once a real vertical
slice exists to validate them against, not before.

## Phase 9 Result

Phase 9 confirms that the two existing pre-canonical implementations do
not contradict the Domain Model in their actual content, only in
documentation that had not yet been reconciled with the canonical
vocabulary (see updated READMEs in `implementations/reference/` and
`implementations/platforms/obsidian/vault/`). It records the seams any
future implementation must respect, and the decision to build that
implementation in Python, targeting Obsidian.

```text
Canonical Models
        ↓
Implementation Boundaries
        ↓
A Vertical Slice (first real code)
        ↓
Implementation Architecture (testing, error handling, configuration, composition)
```

This expresses semantic dependency only; it is not runtime order, data
flow, or a mandate to build in this sequence.
