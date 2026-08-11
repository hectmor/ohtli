# Current Representation

## Purpose

The Current Representation defines the canonical representation currently
accepted by Ohtli for a Represented Instance.

It defines how the current representation persists conceptually, how partial
representation is treated, and how projections relate to the canonical
representation.

It does not define domain semantics, state semantics, relationship semantics,
historical semantics, workflow semantics, or presentation behavior.

---

# Canonical Current Representation

A Represented Instance has one canonical Current Representation.

```text
Represented Instance
        │
        ▼
Canonical Current Representation
```

The identity of the Represented Instance persists while its Current
Representation may change over time.

A change does not create a new Represented Instance or a new Current
Representation identity.

```text
Represented Instance α
        │
        ▼
Current Representation
        │
        ├── updated State
        └── updated Relationships
```

Historical occurrences of changes are handled by the canonical historical
mechanism rather than by creating additional Representation Instances.

---

# Current Representation Semantics

Current Representation means:

> The canonical representation currently accepted by Ohtli as the current
> representation of a Represented Instance.

Current does not mean:

- latest observed information;
- latest modified file;
- latest external information;
- entirely authoritative information.

The authority status of individual represented values is determined by their
applicable canonical contracts.

Therefore:

```text
Current
    ≠ Latest Observed

Current
    ≠ Latest Modified

Current
    ≠ Entirely Authoritative
```

---

# Representation Core

The Current Representation contains the Representation Core defined by the
Representation Model.

```text
Current Representation
│
└── Representation Core
    ├── Identity
    └── Architectural Type
```

The identity identifies the represented instance.

The architectural type identifies the canonical type of the represented
instance.

---

# Represented State

The Current Representation may contain the represented state defined by the
canonical State Model.

```text
Current Representation
│
└── Represented State
    ├── Authoritative State
    └── Derived State
```

Current Representation carries state representation but does not redefine
state semantics.

The authority status of individual values remains governed by the applicable
State contracts.

---

# Current Relationships

The Current Representation may contain the currently applicable relationships
defined by the Interaction Model.

```text
Current Representation
│
└── Current Relationships
    └── Relationship Instances
```

Relationship semantics remain owned by the Interaction Model.

The Current Representation does not redefine:

- Relationship Types;
- relationship meaning;
- cardinality;
- uniqueness;
- relationship constraints.

---

# Partial Representation

A Current Representation may be partial.

A representation does not need to contain every possible piece of information
about a Represented Instance in order to be current.

For example:

```text
Current Representation
│
├── Identity = α
├── Type = Project
└── Lifecycle = Active
```

The absence of a represented element does not by itself assert:

- semantic absence;
- an `Unknown` value;
- invalidity;
- completeness failure.

Therefore:

```text
Partial Representation
    ≠ Invalid Representation

Not Represented
    ≠ Absent

Not Represented
    ≠ Unknown
```

Completeness and validity are determined by the applicable canonical
contracts.

---

# Partial Relationships

If a relationship is not represented in the Current Relationship Set, this
does not automatically establish that the relationship does not exist.

```text
No Current Relationship Representation
    ≠
Explicit Semantic Absence
```

Explicit absence is only meaningful when supported by the applicable
canonical contract.

---

# Validity

A partial Current Representation may still be valid.

```text
Partial
    → degree of represented information

Valid
    → satisfies applicable contracts
```

These are independent properties.

A representation can therefore be:

```text
Current + Partial + Valid
```

---

# Freshness and Staleness

Freshness and staleness are not universal properties of the Representation
Model.

The Current Representation represents what Ohtli currently accepts as the
canonical representation.

Information about external freshness, source freshness, temporal freshness,
stale observations, or synchronization status belongs to the applicable
source, processing, or historical mechanisms.

Therefore:

```text
Freshness
    ≠ Representation State

Staleness
    ≠ Universal Representation State
```

---

# History and Versioning

The Representation Model does not create a representation version for every
change.

It does not define universal:

```text
Representation Version
Representation Snapshot
Representation History
```

A change may produce a historical Event or another canonical historical
record, but the Current Representation remains the current representation of
the same Represented Instance.

```text
Represented Instance α
        │
        ▼
Current Representation
        │
        │ changes
        ▼
Historical Mechanism
```

Therefore:

```text
Current Representation
    ≠ Historical Record
```

---

# Projections

A Represented Instance has one canonical Current Representation.

Alternative physical, serialized, or presentation-oriented forms are
projections of that representation.

```text
Canonical Current Representation
        │
        ├── Markdown Projection
        ├── Database Projection
        ├── API Projection
        └── Other Projection
```

These projections do not constitute independent Current Representations.

Projections do not become independent sources of semantic authority.

---

# Projection Semantics

A Projection is a representation-level transformation of the canonical Current
Representation for a particular purpose.

```text
Current Representation
        │
        ▼
Projection
```

A Projection may:

- select information;
- transform information;
- aggregate information;
- include authorized derived information;
- prepare information for presentation or exchange.

A Projection does not redefine the semantics of the canonical representation.

---

# Derived Projection Information

A Projection may contain derived information computed from the canonical
representation or from other explicitly authorized canonical sources.

For example:

```text
Current Representation
├── Lifecycle = Active
├── Relationships
└── Tasks
        │
        ▼
Project Dashboard Projection
├── Lifecycle = Active
├── Completion = 73%
└── Risk = High
```

Derived projection information does not automatically become part of the
Current Representation.

```text
Derived Projection Data
    ≠
Derived State
```

Information becomes part of the canonical representation only when explicitly
accepted through the applicable canonical model.

---

# Read-only Projections

A read-only Projection consumes the Current Representation without proposing
changes to it.

```text
Current Representation
        │
        ▼
Read-only Projection
        │
        ▼
View / Consumer
```

A read-only Projection cannot become a source of canonical semantic authority.

---

# Writable Projections

A Projection may be writable.

A writable Projection may propose changes to the canonical Current
Representation, but it does not possess authority to apply semantic changes
independently of the applicable canonical contracts.

The conceptual flow is:

```text
Writable Projection
        │
        ▼
Interpretation
        │
        ▼
Validation
        │
        ▼
Authorized Transformation
        │
        ▼
Canonical Current Representation
```

A writable Projection therefore does not bypass:

- State contracts;
- Interaction contracts;
- Workflow authorization;
- Event semantics;
- other applicable canonical constraints.

---

# Projection Validation

Information written through a Projection must be interpreted according to the
canonical model before becoming authoritative.

For example:

```text
Projection
    lifecycle = on_hold
```

does not by itself establish:

```text
Canonical State
    lifecycle = On Hold
```

The proposed change must satisfy the applicable canonical contract.

An invalid projection value does not become canonical state.

```text
Projection Input
        │
        ▼
Interpretation
        │
        ▼
Validation
        │
        ├── invalid → rejected
        │
        └── valid
              │
              ▼
      Authorized Transformation
```

---

# Projection and Workflow

A writable Projection may initiate a change, but it does not redefine or
replace the Workflow Model.

When a change requires workflow authorization, the workflow remains the
authority for the transformation.

```text
Writable Projection
        │
        ▼
Proposed Change
        │
        ▼
Workflow / Canonical Contract
        │
        ▼
Current Representation
```

Therefore:

```text
Projection
    ≠ Workflow
```

---

# Projection and View

Projection and View are distinct architectural concepts.

A Projection is a representation-level transformation.

A View is the presentation layer that consumes a Projection.

```text
Canonical Current Representation
              │
              ▼
         Projection
              │
              ▼
             View
              │
              ▼
            User
```

A View does not own canonical data.

This preserves the architectural principle:

> Views never own data.

---

# View Boundary

Views may consume:

- direct projection data;
- derived projection data;
- formatted projection data.

Views do not redefine canonical semantics.

Therefore:

```text
View
    ≠ Projection
    ≠ Current Representation
```

A View is presentation, not semantic authority.

---

# Architectural Separation

```text
Domain Model
    │
    ▼
Represented Instance
    │
    ▼
Canonical Current Representation
    │
    ├── Representation Core
    ├── Represented State
    └── Current Relationships
             │
             ▼
         Projection
             │
             ▼
            View
             │
             ▼
            User
```

For writable interactions:

```text
User
  │
  ▼
Writable Projection
  │
  ▼
Interpretation
  │
  ▼
Validation
  │
  ▼
Authorized Transformation
  │
  ▼
Canonical Current Representation
```

Historical information remains separate:

```text
Current Representation
        │
        │ changes
        ▼
Historical Mechanism
```

---

# Invariants

## Current Representation

- Every Represented Instance has one canonical Current Representation.
- Current Representation belongs to the same Represented Instance identity.
- Changes do not create a new Represented Instance.
- Current does not mean latest observed.
- Current does not mean latest modified.
- Current does not mean entirely authoritative.

## Partiality

- Current Representation may be partial.
- Partiality does not imply invalidity.
- Absence of representation does not imply semantic absence.
- Absence of representation does not imply an `Unknown` value.
- Completeness is determined by applicable canonical contracts.

## Temporal Semantics

- Freshness is not a universal Representation property.
- Staleness is not a universal Representation State.
- Representation Model does not define universal versioning.
- Representation Model does not define Representation History.
- Historical occurrences belong to the canonical historical mechanism.

## Projections

- A Represented Instance has one canonical Current Representation.
- Alternative physical or presentation forms are projections.
- Projections do not constitute independent Current Representations.
- Projections do not become independent semantic authorities.
- Projections may contain authorized derived information.

## Writable Projections

- Projections may be read-only or writable.
- A writable Projection proposes changes.
- A writable Projection does not independently authorize semantic changes.
- Proposed changes must be interpreted and validated.
- Authorized transformations remain governed by applicable canonical contracts.
- Workflows are not redefined by Projections.

## Views

- Views consume Projections.
- Views do not own canonical data.
- Views do not redefine canonical semantics.
- Views are presentation, not semantic authority.

---

# Scope

This document defines:

- the meaning of Current Representation;
- one Current Representation per Represented Instance;
- partial representation;
- temporal and historical boundaries;
- Projection semantics;
- writable and read-only Projections;
- derived Projection information;
- the Projection-to-View boundary.

It does not define:

- domain semantics;
- state semantics;
- relationship semantics;
- event semantics;
- workflow semantics;
- provenance semantics;
- concrete storage schemas;
- serialization formats;
- filesystem layouts;
- UI implementation;
- universal representation versioning;
- universal freshness or staleness models.
