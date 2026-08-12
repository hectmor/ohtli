# Representation Model

## Purpose

The Representation Model defines how canonical Ohtli semantics are represented
while remaining independent of implementation technology.

It provides the representation contracts connecting the canonical Phase 3
models with future implementations.

The Representation Model represents canonical semantics; it does not redefine
them.

```text
Canonical Phase 3 Models
        │
        ▼
Representation Model
        │
        ▼
Implementation
```

---

# Scope

The Representation Model consolidates:

- representation foundations;
- Current Representation;
- State Representation;
- Relationship Representation;
- Event Representation;
- Workflow-Facing Representation;
- Representation Invariants.

It defines representation boundaries without defining implementation
technology, storage schemas, APIs, UI, navigation, automation, or execution
technology.

---

# Core Representation

A Represented Instance has one canonical Current Representation.

```text
Represented Instance
        │
        ▼
Canonical Current Representation
        │
        ├── Representation Core
        ├── Represented State
        └── Current Relationships
```

The Current Representation is the representation currently accepted by Ohtli
for that Represented Instance.

Current does not mean latest observed, latest modified, or entirely
authoritative.

A Current Representation may be partial.

```text
Partial Representation
    ≠ Invalid Representation

Not Represented
    ≠ Semantic Absence
```

---

# Representation Core

The Representation Core provides the stable architectural identity and type
information required to identify a Represented Instance.

Identity is independent of physical representation.

```text
Represented Instance α
        │
        ├── rename
        ├── relocation
        ├── archive
        └── reactivate
                │
                ▼
          Identity α
```

Therefore:

```text
Rename       ≠ New Identity
Relocation   ≠ New Identity
Archive      ≠ Identity Destruction
Reactivate   ≠ New Identity
```

---

# State Representation

Current Representation may expose represented State.

```text
Current Representation
│
├── Authoritative State
└── Derived State
```

State semantics remain owned by the canonical State Model.

Derived State must not silently replace Authoritative State.

```text
Derived State
    ≠ Authoritative State
```

Current State does not require reconstruction from Events.

---

# Relationship Representation

Relationships are represented using stable Represented Instance identities.

```text
Stable Identity
      │
      ▼
Relationship Reference
```

The representation preserves the semantics of the canonical Interaction
Model, including applicable:

- relationship meaning;
- direction;
- cardinality;
- uniqueness;
- constraints.

Implementation structure may change without changing relationship semantics.

---

# Event Representation

Events may be represented as historical evidence.

```text
Event
  │
  └── Historical Evidence

Current Representation
  │
  └── Current State
```

Current State and historical evidence are distinct.

```text
Current State
    ≠ Historical Evidence
```

Event Sourcing is not an architectural requirement.

Event replay may be used by an implementation, but Current State must not
require replay of Events.

---

# Workflow-Facing Representation

A Workflow-Facing Representation is a workflow-specific projection of the
canonical Current Representation, potentially incorporating explicitly
authorized Relevant Context.

```text
Canonical Current Representation
             +
Authorized Relevant Context
             │
             ▼
Workflow-Facing Representation
             │
             ▼
Workflow Model
```

The Workflow Model evaluates its own preconditions.

```text
Workflow-Facing Representation
        │
        ▼
Workflow Preconditions
        │
        ▼
Applicable / Not Applicable
```

Applicability does not imply:

```text
Execution
Capability
Authority
```

Inspection does not imply transformation rights.

```text
Inspectable
    ≠ Transformable
```

Workflow transformations must produce results that satisfy applicable
Representation Invariants before they update Current Representation.

Workflow results may be persistent or non-persistent.

---

# Representation Invariants

Every valid Ohtli representation must preserve:

- stable identity across rename and relocation;
- stable identity across lifecycle transitions;
- stable identity across archive and reactivation;
- required historical evidence;
- independence between contextual presence and information accessibility;
- stable identities in relationship references;
- relationship direction and cardinality;
- applicable relationship semantics and constraints;
- historical evidence represented by Events;
- independence of Current State from mandatory Event replay;
- separation of Authoritative and Derived State;
- Representation Invariants across Workflow transformations;
- architectural semantics across implementation technologies;
- representation semantics across execution mechanisms.

Representation invariants are not optional implementation conventions.

---

# Cross-Model Relationship

The Representation Model preserves the semantics of canonical Phase 3 models
without redefining them.

```text
Domain Model ───────┐
Interaction Model ──┤
State Model ────────┤
Event Model ────────┼──→ Representation Model
Workflow Model ─────┘
```

The Representation Model:

- represents Domain Objects without redefining their semantics or lifecycle;
- represents canonical Relationships without changing their meaning;
- represents relevant Events as historical evidence;
- exposes workflow-relevant state;
- preserves representation invariants.

It is therefore a representation boundary, not a semantic authority above the
Phase 3 models.

---

# Archive and Reactivation

Archive changes contextual presence without destroying stable identity.

```text
Identity α
    │
    ├── Active
    ├── Archived
    └── Reactivated
```

Archive must preserve historical evidence required by applicable canonical
historical contracts.

Historical presence does not imply informational inaccessibility.

```text
Historical Presence
    ≠ Informational Inaccessibility
```

---

# Technology Independence

The Representation Model is independent of implementation technology.

The same architectural semantics must be expressible by substantially
different technology families.

Conceptually:

```text
                 Representation Model
                         │
             ┌───────────┴───────────┐
             ▼                       ▼
      Document/File             Relational
       representation          representation
             │                       │
             └───────────┬───────────┘
                         ▼
              Same Architectural Semantics
```

A document/filesystem implementation and a relational/database implementation
may use different physical structures while remaining valid implementations.

Technology may change:

- physical structure;
- storage;
- serialization;
- access mechanism.

Technology may not change:

- identity semantics;
- state semantics;
- relationship semantics;
- historical semantics;
- workflow-facing semantics;
- representation invariants.

```text
Implementation Technology
    ≠ Architectural Semantics
```

---

# Actor Independence

The Representation Model does not depend on a specific execution actor.

It can be used by:

```text
Human
Deterministic System
AI-Assisted System
Hybrid System
```

AI is optional and has no special architectural authority.

Execution mechanism cannot redefine representation semantics.

```text
Execution Mechanism
    ≠ Representation Semantics
```

---

# Representation Boundaries

The architectural boundaries are:

```text
Canonical Models
      │
      ▼
Canonical Current Representation
      │
      ├── State
      ├── Relationships
      └── Historical boundary
      │
      ▼
Workflow-Facing Projection
      │
      ▼
Workflow Model
```

Presentation Views are downstream consumers and do not own canonical data.

```text
Current Representation
        │
        ├── Workflow-Facing Projection
        │          │
        │          ▼
        │       Workflow
        │
        └── Presentation Projection
                   │
                   ▼
                  View
```

---

# Detailed Contracts

The detailed Representation Model contracts are:

- [Representation Foundations](representation-foundations.md)
- [State Representation](state-representation.md)
- [Relationship Representation](relationship-representation.md)
- [Event Representation](event-representation.md)
- [Workflow-Facing Representation](workflow-facing-representation.md)
- [Representation Invariants](representation-invariants.md)

These documents provide detailed contracts; this README is the canonical entry
point and consolidated architectural view.

---

# Consistency Rule

Issue #7 consolidates and verifies established contracts.

It does not redefine them.

If a genuine contradiction is discovered:

```text
Consolidation
      │
      ▼
Contradiction
      │
      ▼
Identify originating model
      │
      ▼
Resolve in originating model
```

The Representation Model must not silently become a higher-order authority
that overrides canonical Phase 3 semantics.

---

# Technology Independence Test

The model passes the conceptual technology independence test when both a
document/filesystem representation and a relational representation can
express the same:

- stable identities;
- State;
- Relationships;
- historical evidence;
- Workflow-Facing Representation;
- Representation Invariants.

No implementation is required by this test.

The criterion is semantic compatibility, not physical structural identity.

```text
Implementation
      │
      ▼
Semantic Compatibility
      │
      ▼
Representation Invariants
      │
      ├── valid → compatible Ohtli implementation
      └── invalid → incompatible implementation
```

---

# Future Phases

The Representation Model provides the architectural contract for future
phases.

It does not define User Experience or implementation architecture.

Conceptually:

```text
Phase 3
Canonical Models
        │
        ▼
Phase 4
Representation Model
        │
        ▼
Future
User Experience
        │
        ▼
Implementation
```

Future UX and implementation layers must consume and preserve this model
rather than redefine its semantics.

---

# Scope Boundary

This model does not define:

- Markdown schemas;
- YAML schemas;
- filesystem layout;
- database schemas;
- UI;
- navigation;
- UX;
- automation;
- agents;
- APIs;
- implementation architecture.

Those concerns belong to future phases or specialized implementation
contracts.

---

# Phase 4 Completion Criterion

Phase 4 Representation Model is consolidated when:

- all approved representation contracts are internally consistent;
- canonical Phase 3 semantics remain unchanged;
- representation invariants are explicit;
- Workflow-facing representation is defined;
- historical representation does not require Event Sourcing;
- identity survives implementation-level changes;
- at least two technology families can conceptually implement the model;
- no Representation Model concept depends on Markdown, YAML, filesystem,
  databases, or Obsidian.

This README is the canonical entry point for the consolidated Representation
Model.
