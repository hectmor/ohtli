# Relationship Representation

## Purpose

The Relationship Representation defines how canonical relationships between
Ohtli Represented Instances are represented without redefining the semantics
owned by the Interaction Model.

It answers:

> How are currently applicable relationships represented between Represented
> Instances?

The Representation Model provides representational structure. It does not
become a second source of semantic authority.

---

# Architectural Boundary

The authority direction is:

```text
Canonical Interaction Model
        │
        ├── Relationship Types
        ├── Relationship Semantics
        ├── Allowed Endpoints
        ├── Cardinality
        ├── Uniqueness
        └── Semantic Constraints
                │
                ▼
       Relationship Representation
```

The Representation Model represents the relationships defined by the
canonical architecture.

It does not independently define:

- Relationship Types;
- relationship meaning;
- allowed source or target types;
- cardinality;
- uniqueness;
- semantic relationship constraints.

The Representation Model refers to the applicable canonical Relationship Type
rather than maintaining its own normative relationship taxonomy.

---

# Relationship Instance

A Relationship Instance is a representational instance of a canonical
relationship between two Represented Instances.

Conceptually:

```text
Relationship Instance
├── Relationship Identity
├── Relationship Type
├── Source
└── Target
```

A Relationship Instance is not a Domain Object and is not a Represented
Instance.

Therefore:

```text
Relationship Instance ≠ Domain Object
Relationship Instance ≠ Represented Instance
```

---

# Relationship Identity

A Relationship Instance has its own representational identity.

Relationship Identity distinguishes a relationship instance from the
identities of its endpoints.

```text
Represented Instance Identity
    ≠
Relationship Identity
```

Relationship Identity does not by itself determine semantic uniqueness.

---

# Identity and Uniqueness

Identity and uniqueness are separate concepts.

Two Relationship Instances may have distinct identities even when they have
equivalent source, type, and target.

Whether such relationships may coexist is determined by the applicable
Interaction Model contract.

```text
Identity
    → distinguishes instances

Uniqueness Constraint
    → determines valid coexistence
```

Representation Model does not define uniqueness rules.

---

# Relationship Type

Relationship Type is the canonical semantic type of a Relationship Instance.

Examples include canonical types such as:

```text
belongs to
contains
references
supports
```

The authoritative definitions belong to the Interaction Model.

Representation Model uses the canonical type; it does not redefine its
meaning.

---

# Source and Target

A Relationship Instance identifies the Represented Instances participating in
the relationship.

```text
Relationship Instance
├── Source
└── Target
```

The semantic direction is inherited from the canonical Interaction Model.

---

# Current Relationship Representation

A Represented Instance exposes its currently applicable relationships through
a Current Relationship Set.

```text
Represented Instance
│
├── Representation Core
├── Represented State
└── Current Relationships
```

For example:

```text
Project α

Current Relationships
├── ρ₁
│   type   = belongs to
│   target = Area β
│
├── ρ₂
│   type   = references
│   target = Resource γ
│
└── ρ₃
    type   = contains
    target = Meeting δ
```

Current Relationships contain only Relationship Instances currently applicable
to the represented context.

---

# Relationships Are Not State Dimensions

Relationships are not automatically State Dimensions.

For example:

```text
Project α
    belongs to
Area β
```

must not be represented as:

```text
Project α
    State Dimension:
        belongs_to = Area β
```

The relationship remains a semantic connection governed by the Interaction
Model.

Therefore:

```text
Relationship ≠ State Dimension
```

---

# Relationship State

A Relationship Instance may have relationship-specific state when the
applicable Relationship Type Contract defines such state.

```text
Relationship Instance
├── Relationship Identity
├── Relationship Type
├── Source
├── Target
└── optional Relationship State
```

Relationship State is optional.

A relationship does not automatically receive a universal lifecycle or state
model.

If Relationship State exists, its semantics are defined by the applicable
canonical Relationship Type Contract.

Representation Model does not introduce a universal Relationship Lifecycle.

---

# Relationship State and Represented State

Relationship State does not automatically inherit the full State Representation
defined for a Represented Instance.

Therefore:

```text
Relationship State
    ≠ Represented State
```

A change in Relationship State does not imply a change in the Lifecycle or
Contextual Presence of either endpoint.

---

# Provenance References

A Relationship Instance may contain references to provenance.

```text
Relationship Instance
│
└── Provenance References
```

Provenance may identify one or more canonical sources supporting the existence
or interpretation of a relationship.

For example:

```text
ρ₁
Project α
references
Resource β

Provenance
├── Meeting γ
├── Journal Entry δ
└── Event ε
```

Provenance is represented through references. The Representation Model does
not define provenance as a new Domain Object and does not define provenance
semantics itself.

Therefore:

```text
Provenance
    ≠ Relationship
    ≠ Relationship State
    ≠ Domain Object
```

---

# Multiple Provenance Sources

A Relationship Instance may have zero, one, or multiple provenance references
when permitted by the applicable architectural contract.

Adding provenance does not by itself change the identity of the relationship.

---

# Derived Origin

A Relationship Instance may be directly asserted or derived from other
canonical information.

The Representation Model does not introduce a separate:

```text
Derived Relationship
```

category.

For example, relationships ρ₁ and ρ₂ may support a derived relationship ρ₃.
ρ₃ remains a normal canonical Relationship Instance, while its provenance may
record the information from which it was derived.

Therefore:

```text
Relationship Semantics
    → what the relationship means

Provenance
    → how the relationship is supported or derived
```

---

# Relationship Changes

A Relationship Instance represents a particular semantic relationship.

When a change affects the elements that constitute the relationship's
semantic identity according to its applicable Relationship Type Contract, the
new relationship is represented as a distinct Relationship Instance.

For example:

```text
ρ₁
Project α
belongs to
Area β
```

may be replaced by:

```text
ρ₂
Project α
belongs to
Area γ
```

The Representation Model does not prescribe a universal technical formula for
relationship identity.

The applicable relationship contract determines which changes are
semantically identity-changing.

---

# Relationship Absence

The absence of a relationship is not represented as a Relationship State.

If a Relationship Instance is no longer currently applicable:

```text
ρ₁ ∉ Current Relationship Set
```

The representation does not require:

```text
ρ₁
    state = Absent
```

Therefore:

```text
Relationship Absence
    ≠ Relationship State
    ≠ Representation Condition
```

Absence is represented by membership or non-membership in the Current
Relationship Set.

---

# Current Relationships and History

The Representation Model represents currently applicable relationships.

Historical relationship occurrences are not automatically retained as part
of the Current Relationship Set.

Historical evidence belongs to the Event Model or another canonical historical
mechanism.

Therefore:

```text
Current Relationship Representation
        ≠
Historical Evidence
```

The Representation Model does not introduce a universal Relationship History
or Event Sourcing mechanism.

---

# Relationship and Events

A change to a relationship may be associated with an Event.

However:

```text
Relationship Instance
    ≠ Event

Relationship Change
    ≠ Event
```

The Event Model defines historical occurrence semantics. The Representation
Model defines the resulting current relationship representation.

---

# Relationship and Workflows

A Workflow may create, remove, replace, or otherwise transform relationships
when authorized by its canonical workflow contract.

The Representation Model does not define workflow applicability or execution.

```text
Workflow
    │
    ▼
Relationship Transformation
    │
    ▼
Current Relationship Representation
```

Therefore:

```text
Relationship
    ≠ Workflow
```

---

# Relationship and Domain Model

Relationship Representation does not introduce new domain concepts.

A relationship connecting domain concepts is not itself a new domain object.

The fact that a Relationship Instance has identity, optional state, or
provenance does not change its architectural category.

---

# Relationship and Interaction Model

The separation can be summarized as:

```text
Interaction Model
│
├── Relationship Type
├── Meaning
├── Allowed endpoints
├── Direction
├── Cardinality
├── Uniqueness
└── Semantic constraints
        │
        ▼
Relationship Representation
│
├── Relationship Identity
├── Relationship Type Reference
├── Source
├── Target
├── Optional Relationship State
└── Provenance References
```

The Representation Model never becomes the authority for the semantic
relationship itself.

---

# Examples

## Project belongs to Area

```text
Project α

Current Relationships
└── ρ₁
    ├── type   = belongs to
    ├── source = α
    └── target = Area β
```

The Interaction Model determines whether this configuration satisfies the
`belongs to` constraints.

## Project references Resource

```text
Project α

Current Relationships
└── ρ₂
    ├── type   = references
    ├── source = α
    ├── target = Resource β
    └── provenance
        └── Meeting γ
```

## Relationship replacement

Initial:

```text
ρ₁
Project α
    belongs to
Area β
```

Current after semantic change:

```text
ρ₂
Project α
    belongs to
Area γ
```

The old relationship is not required to remain in the Current Relationship
Set. Historical evidence is governed elsewhere.

## Derived relationship

```text
ρ₁
Project α
    references
Meeting γ

ρ₂
Meeting γ
    references
Resource β
```

A canonical derivation may support:

```text
ρ₃
Project α
    references
Resource β
```

`ρ₃` is not a new `Derived Relationship` category. Its provenance may record
the information from which it was derived.

---

# Invariants

## Architectural Authority

- Relationship semantics belong to the Interaction Model.
- Representation Model does not redefine Relationship Types.
- Cardinality and uniqueness remain outside Representation Model.
- Relationship constraints are inherited from canonical architectural contracts.

## Identity

- Every Relationship Instance has representational identity.
- Relationship Identity is distinct from endpoint identities.
- Identity and semantic uniqueness are distinct concepts.
- Relationship identity is not defined by a universal technical formula.

## Structure

- A Relationship Instance has a canonical Relationship Type.
- A Relationship Instance identifies a Source and Target.
- Relationship direction is inherited from the Interaction Model.
- A Relationship Instance is not a Domain Object.
- A Relationship Instance is not a Represented Instance.

## Relationship State

- Relationship State is optional.
- Relationship State exists only when defined by the applicable Relationship
  Type Contract.
- Relationship State does not inherit the full Represented State model.
- Representation Model does not define a universal Relationship Lifecycle.

## Provenance

- Provenance is represented through references.
- Multiple provenance references may be represented.
- Provenance is not a Domain Object introduced by Representation Model.
- Provenance does not redefine relationship semantics.
- Derived origin does not create a separate Derived Relationship category.

## Current Representation

- Current Relationship Set contains currently applicable relationships.
- A relationship that is no longer applicable is absent from the current set.
- Relationship Absence is not a Relationship State.
- Relationship Absence is not a Representation Condition.

## History

- Current Relationship Representation is distinct from Historical Evidence.
- Representation Model does not define Relationship History.
- Historical relationship occurrences belong to the canonical historical
  mechanism.
- Relationship Instance is distinct from Event.

## Workflow

- Workflows may transform relationships when authorized.
- Representation Model does not define workflow applicability or execution.

---

# Scope

This document defines how canonical relationships are represented.

It does not define:

- new Relationship Types;
- relationship semantics;
- cardinality;
- uniqueness;
- workflow semantics;
- Event semantics;
- provenance semantics;
- concrete storage schemas;
- serialization formats;
- filesystem layouts;
- user-interface behavior;
- a universal Relationship Lifecycle;
- Event Sourcing;
- new Domain Objects.
