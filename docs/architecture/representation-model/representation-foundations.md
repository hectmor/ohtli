# Representation Foundations

## Purpose

The Representation Foundations define the conceptual basis for representing Ohtli architectural concepts as system state.

The Representation Model establishes the boundary between the canonical architectural semantics defined by Ohtli and the concrete technologies that may later implement them.

It answers the foundational question:

> How can an architectural concept exist as stable, identifiable, inspectable, and transformable Ohtli System State without depending on a particular implementation technology?

This document defines representation, represented instances, representation contracts, identity, architectural type, represented state, represented values, continuity, and persistence boundaries.

It does not define the detailed structure of state, relationships, Events, or workflow-facing representation. Those concerns are defined by subsequent parts of the Representation Model.

---

# Architectural Boundary

Ohtli distinguishes three architectural levels:

```text
Canonical Architectural Models
            │
            │ define semantics
            ▼
     Representation Model
            │
            │ defines representation contracts
            ▼
    Concrete Implementation
```

The canonical architectural models define what Ohtli concepts mean.

The Representation Model defines how those concepts can manifest as Ohtli System State while preserving their architectural semantics.

Concrete implementations determine how those representations are physically realized.

Therefore:

```text
Architectural Concept != Representation
Representation != Implementation
```

Representation must not redefine the architectural semantics established by the canonical models.

---

# Representation

A Representation is the technology-independent manifestation of an architectural concept within Ohtli System State, through which that concept can be identified, inspected, related, and transformed according to its architectural contracts.

Representation provides the architectural boundary between semantic concepts and their concrete realization.

It does not prescribe how information is serialized, stored, indexed, displayed, or transported.

A Representation therefore does not imply any particular use of:

- Markdown;
- YAML;
- filesystem structures;
- relational databases;
- document databases;
- object stores;
- programming-language objects;
- APIs;
- user interfaces.

These belong to implementation.

---

# Representation Contract

A Representation Contract defines the representation requirements applicable to a represented architectural concept.

It combines:

1. the general requirements established by the Representation Model; and
2. the relevant contracts established by the canonical architectural models.

Conceptually:

```text
General Representation Requirements
                +
Applicable Architectural Contracts
                │
                ▼
       Representation Contract
```

A Representation Contract does not duplicate or redefine canonical architectural contracts. It preserves them.

Therefore:

```text
Representation Contract != Architectural Concept
Representation Contract != Represented Instance
```

---

# Represented Instance

A Represented Instance is a concrete occurrence of an architectural concept for which independent identity and continuity are required.

A Represented Instance satisfies the Representation Contract applicable to the architectural concept it instantiates.

```text
Architectural Concept
        │
        ▼
Representation Contract
        │
        │ satisfied by
        ▼
Represented Instance
```

A Represented Instance is not necessarily a Domain Object. Other architectural concepts may qualify as Represented Instances when their architectural contracts require independent identity and continuity.

The Representation Model must never introduce new architectural concepts merely because an implementation requires something to store.

---

# Representation Core

Every Represented Instance contains a stable Representation Core.

```text
Representation Core
├── Identity
└── Architectural Type
```

These properties remain invariant throughout the continuity of the Represented Instance.

Identity answers which represented instance this is. Architectural Type answers what architectural concept this instance instantiates.

The Representation Core is distinct from Represented State.

---

# Identity

Every Represented Instance has a stable identity. Identity establishes continuity across changes to mutable represented information.

Identity is independent of mutable or implementation-specific properties.

```text
Identity != Title
Identity != Name
Identity != Filename
Identity != Filesystem Path
Identity != Lifecycle State
Identity != Contextual Presence
```

Rename, relocation, lifecycle transition, relationship changes, Archive, and Reactivate do not change identity.

Identity identifies continuity rather than current state or semantic description.

---

# Global Identity

Represented Instance identity is globally unique across Ohtli Systems. Two independently created Represented Instances must not share the same identity.

The Representation Model requires global uniqueness but does not prescribe the mechanism used to achieve it. It does not require UUID, ULID, URI, integer identifiers, or centralized identity allocation.

Global identity does not by itself define copying, replication, synchronization, federation, or conflict resolution.

---

# Architectural Type

Every Represented Instance has a stable Architectural Type.

Architectural Type identifies the canonical architectural concept instantiated by the Represented Instance.

```text
Identity = α
Architectural Type = Project
```

Identity answers which instance this is; Architectural Type answers what architectural concept it instantiates.

Architectural Type is semantically meaningful but independent from Identity.

```text
Architectural Type != Identity
Architectural Type != Lifecycle State
Architectural Type != Directory
Architectural Type != Filename
Architectural Type != Database Table
Architectural Type != User Interface View
```

Architectural Type must not be inferred from storage location or implementation structure and remains invariant throughout the continuity of a Represented Instance.

A transition such as `Project → Area` is therefore not a state transition of the same Represented Instance.

---

# Represented State

A Represented Instance consists conceptually of:

```text
Represented Instance
├── Representation Core
└── Represented State
```

The Representation Core is stable. Represented State contains represented information that may vary throughout the lifetime of the instance according to applicable architectural contracts.

The detailed structure and semantics of Represented State are intentionally not defined here. They belong to the State Representation model.

---

# Represented Values

Not every piece of represented information requires independent architectural identity.

A Represented Value is information within represented system state that does not require independent architectural identity.

```text
Represented Instance
│
├── Representation Core
│   ├── Identity = α
│   └── Architectural Type = Project
│
└── Represented State
    ├── title = "Ohtli"
    ├── lifecycle = Active
    └── contextual presence = Operational
```

The Project is a Represented Instance. The individual state values do not automatically become independent Represented Instances.

---

# Representation and Persistence

Representation and persistence are independent architectural concerns.

A Represented Instance may be persistent or transient when its architectural contract requires independent identity and meaningful continuity.

```text
Representation != Persistence
Identity != Persistence
Continuity != Durable Storage
```

Persistence is not sufficient to make information a Represented Instance, and transient information does not automatically become one. The determining criterion is the applicable architectural contract.

---

# Continuity

Continuity means that the identity of a Represented Instance remains invariant throughout its semantically relevant lifetime. It does not inherently require durable storage.

For a Represented Instance `x`:

```text
Core(x, t1) = Core(x, t2)
```

while:

```text
State(x, t1) != State(x, t2)
```

may be valid.

---

# Representation Transformation

A valid transformation of a Represented Instance changes its Represented State while preserving its Representation Core.

```text
Before
Instance α
├── Core = C
└── State = S1

        │ valid transformation
        ▼

After
Instance α
├── Core = C
└── State = S2
```

Equivalently:

```text
(α, T, S1) → (α, T, S2)
```

where `α` is the stable global Identity, `T` is the stable Architectural Type, and `S1` and `S2` are valid represented states.

---

# Authority Direction

Representation is constrained by architecture. Implementation is constrained by representation.

```text
Canonical Architectural Models
            │
            ▼
     Representation Model
            │
            ▼
    Concrete Implementation
```

An implementation requirement cannot silently create or redefine an architectural concept. If representation exposes a missing architectural concept, the inconsistency must be resolved in the appropriate canonical architectural model.

---

# Technology Independence

The Representation Model must remain independent of concrete technology.

Different implementations may organize and persist information differently while satisfying the same Representation Contracts.

```text
                 Representation Contract
                         │
               ┌─────────┴─────────┐
               ▼                   ▼
        Implementation A    Implementation B
         Markdown/YAML          Database
               │                   │
               └─────────┬─────────┘
                         ▼
              same architectural semantics
```

Storage technology must never redefine architectural meaning.

---

# Foundational Invariants

## Identity

- Every Represented Instance has stable identity.
- Identity is globally unique across Ohtli Systems.
- Identity is independent of mutable represented information and concrete implementation.
- Rename, relocation, lifecycle transitions, Archive, and Reactivate do not change identity.

## Architectural Type

- Every Represented Instance has an Architectural Type.
- Architectural Type identifies its canonical architectural concept.
- Architectural Type is independent of Identity.
- Architectural Type remains stable throughout instance continuity.
- Architectural Type is not determined by storage location or implementation structure.

## Representation Structure

- A Represented Instance consists conceptually of a Representation Core and Represented State.
- Representation Core contains Identity and Architectural Type.
- Representation Core remains stable throughout instance continuity.
- Represented State may change according to applicable architectural contracts.
- Not every Represented Value is a Represented Instance.

## Architectural Authority

- Representation does not redefine architectural semantics.
- Representation requirements derive from canonical architectural contracts.
- Representation Model does not introduce architectural concepts to satisfy implementation needs.
- Concrete implementations must preserve Representation Model contracts.

## Persistence

- Representation does not imply persistence.
- Persistence does not imply independent architectural identity.
- Continuity does not inherently require durable storage.

---

# Scope

This document defines only the foundations of the Representation Model.

It intentionally does not define:

- authoritative versus derived state;
- detailed lifecycle representation;
- Contextual Presence representation;
- relationship representation or identity;
- Event representation, identity, or provenance;
- workflow-observable state;
- serialization formats;
- storage schemas;
- filesystem layouts;
- user interfaces;
- automation mechanisms;
- AI agents.

These concerns belong to subsequent Representation Model documents or later architectural phases.

---

# Summary

```text
Canonical Architectural Models
            │
            ▼
    Architectural Concept
            │
            ▼
   Representation Contract
            │
            ▼
    Represented Instance
            │
       ┌────┴────┐
       ▼         ▼
Representation  Represented
    Core           State
       │             │
   ┌───┴───┐         ▼
   ▼       ▼      Represented
Identity  Type       Values
   │       │
 stable  stable
 global  semantic

            │
            ▼
   Concrete Implementation
```

This structure establishes the stable boundary required for subsequent state, relationship, Event, and workflow-facing representation contracts.
