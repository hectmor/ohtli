# Representation Invariants

## Purpose

Representation Invariants define the properties that every valid Ohtli representation must preserve independently of implementation technology.

They provide the compatibility contract between the architecture and future implementations.

These invariants consolidate constraints established by the Domain, Interaction, State, Event, Workflow, and Representation Models.

---

# Stable Identity

A Represented Instance has a stable identity independent of its physical representation.

The identity survives rename, relocation, storage migration, lifecycle transitions, archival, and reactivation.

```text
Represented Instance α
        │
        ├── rename
        ├── relocation
        ├── lifecycle transition
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

# Lifecycle and Identity

Lifecycle transitions change the state of a Represented Instance without changing its stable identity.

```text
Represented Instance α
        │
        ├── Created
        ├── Active
        ├── On Hold
        ├── Completed
        └── ...
                │
                ▼
           Identity α
```

Therefore:

```text
Lifecycle Transition
    ≠ Identity Change
```

---

# Archive and Historical Evidence

Archiving changes contextual presence but does not destroy stable identity.

Archive must preserve the historical evidence required by the applicable canonical Event Model and other established historical contracts.

```text
Active
  │
  ▼
Archive
  │
  ├── Identity preserved
  ├── Required historical evidence preserved
  └── Contextual presence changed
```

Archive does not imply informational inaccessibility.

---

# Contextual Presence and Accessibility

Contextual presence and information accessibility are independent properties.

```text
Historical Presence
        │
        ├── information accessible
        └── information restricted
```

Therefore:

```text
Historical Presence
    ≠ Informational Inaccessibility
```

---

# Stable Relationship References

Relationships must reference stable Represented Instance identities and remain valid across implementation-level rename, relocation, and storage migration.

```text
Stable Identity
      │
      ▼
Relationship Reference
      │
      ├── rename
      ├── relocation
      └── storage migration
             │
             ▼
       Same Relationship
```

---

# Relationship Semantics

A valid representation must preserve the semantics defined by the Interaction Model, including applicable:

- relationship type;
- direction;
- cardinality;
- uniqueness;
- constraints;
- semantic meaning.

The implementation may change representation structure, but not relationship semantics.

```text
Representation
      │
      ▼
Interaction Model
      │
      ├── direction
      ├── cardinality
      ├── uniqueness
      └── meaning
```

---

# Historical Evidence

Events preserve the historical evidence required by the canonical Event Model.

Current State does not replace historical evidence.

```text
Event
  │
  └── Historical Evidence

Current Representation
  │
  └── Current State
```

Therefore:

```text
Event
    ≠ Current State

Current State
    ≠ Historical Evidence
```

---

# Current State Independence

Current State must not require reconstruction from Events.

Events may explain or evidence how current state came to exist, but they are not the sole source from which Current State must be derived.

```text
Current Representation
        │
        └── Current State

Event Model
        │
        └── Historical Evidence
```

Event replay may be used as an implementation technique, but event sourcing is not an architectural requirement.

---

# Authoritative and Derived State

Authoritative State and Derived State remain distinct.

```text
Current Representation
│
├── Authoritative State
│
└── Derived State
```

Derived State must not silently replace Authoritative State.

A change in authority requires an explicit transformation accepted by the applicable canonical contract.

```text
Derived State
      │
      │ explicit transformation
      ▼
Authoritative State
```

---

# Workflow Transformations

Workflow transformations must preserve all applicable Representation Invariants.

```text
Workflow
    │
    ▼
Transformation Result
    │
    ▼
Representation Invariants
    │
    ├── valid → accepted
    └── invalid → rejected
```

A Workflow cannot redefine, bypass, or create exceptions to architectural Representation Invariants.

```text
Workflow
    → Transformation Semantics

Representation
    → Representation Invariants
```

---

# Technology Independence

Implementation technology may change representation structure, storage, or serialization, but must not change architectural semantics.

```text
Markdown / YAML
       │
       ├──────────────┐
       │              │
       ▼              ▼
PostgreSQL          Other Storage
       │              │
       └───────┬──────┘
               ▼
      Architectural Semantics
```

A valid implementation preserves canonical semantics and invariants regardless of physical representation.

```text
Implementation Technology
    ≠
Architectural Semantics
```

---

# Execution Independence

The mechanism that executes a Workflow must not redefine representation semantics.

The same representation contract may be used by:

```text
Human
Deterministic System
AI-Assisted System
Hybrid System
```

Therefore:

```text
Execution Mechanism
    ≠
Representation Semantics
```

AI is optional and has no special architectural authority.

---

# Cross-Model Compatibility

A valid representation must remain compatible with the canonical models.

```text
Representation
     │
     ├── Domain Model
     ├── State Model
     ├── Interaction Model
     ├── Event Model
     └── Workflow Model
```

Representation may carry information defined by these models, but must not redefine their semantics.

---

# Compatibility Contract

The Representation Invariants provide a technology-independent compatibility contract.

An implementation is valid when its behavior preserves the invariants defined by the architecture.

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

A Markdown/YAML implementation and a PostgreSQL implementation can therefore be evaluated against the same architectural contract.

---

# Invariant Summary

A valid Ohtli representation must preserve:

- stable identity across rename and relocation;
- stable identity across lifecycle transitions;
- stable identity across archive and reactivation;
- required historical evidence during archive;
- independence between contextual presence and information accessibility;
- stable identities in relationship references;
- relationship direction;
- relationship cardinality;
- applicable relationship semantics and constraints;
- historical evidence represented by Events;
- independence of Current State from mandatory Event replay;
- separation of Authoritative State and Derived State;
- Representation Invariants across Workflow transformations;
- architectural semantics across implementation technologies;
- representation semantics across execution mechanisms.

---

# Scope

This document consolidates constraints derived from the already approved architecture and Representation Model decisions.

It does not introduce:

- Domain Objects;
- relationships;
- Events;
- workflows;
- lifecycle states;
- representation technologies;
- storage schemas;
- execution technologies.
