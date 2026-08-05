# Interaction Model

## Purpose

The Interaction Model defines the semantic relationships between the
Domain Objects of Ohtli.

It answers a single question:

> How are Domain Objects related?

The Interaction Model defines:

- relationship meaning;
- relationship direction;
- relationship cardinality when multiplicity is part of the semantic
  contract.

The Interaction Model does not define workflows, events, Object
lifecycles, behavioral business rules, or implementation details.

---

# Design Principles

## Semantic Relationships

Relationships describe semantic connections between Domain Objects.

Every relationship has an explicit meaning.

Generic relationships such as `relates to` are not allowed.

---

## Technology Independent

Relationships exist independently of any implementation technology.

Whether objects are stored as Markdown files, database records, or any
other representation does not change the conceptual model.

---

## Object-Centered

Relationships always connect Domain Objects.

Processes, workflows, and events do not participate in the Interaction
Model.

---

## Directional

Relationships are defined from one object toward another.

Direction expresses meaning, not implementation.

For example:

```text
Project
    belongs to
Area
```

and:

```text
Area
    contains
Project
```

express different semantic perspectives even when they describe related
domain structure.

---

## Cardinality

Relationships may define cardinality when multiplicity is part of their
semantic meaning.

Cardinality describes the allowed structural relationship between
Domain Objects.

For example:

```text
Project
    belongs to
Area (0..1)
```

means that a Project may belong to at most one Area.

Similarly:

```text
Area
    contains
Project (0..*)
```

means that an Area may contain zero or more Projects.

Cardinality is part of the semantic relationship contract.

It does not define behavioral business rules or implementation-specific
constraints.

---

# Relationship Types

## belongs to

Represents contextual ownership.

Example:

```text
Project
    belongs to
Area
```

`belongs to` identifies the Domain Object that provides the broader
domain context for another object.

---

## contains

Represents logical organization.

Example:

```text
Area
    contains
Project
```

`contains` expresses logical membership or organization.

It does not imply physical storage containment.

---

## references

Represents an explicit semantic reference from one Domain Object to
another.

Example:

```text
Project
    references
Resource
```

A reference does not imply dependency or ownership.

---

## supports

Represents knowledge or context provided by one Domain Object to
another.

Example:

```text
Resource
    supports
Project
```

Support is conceptual rather than structural.

It does not imply ownership or lifecycle dependency.

---

# Domain Relationships

## Project

belongs to

- Area (0..1)

contains

- Meeting (0..*)

references

- Reference (0..*)
- Resource (0..*)
- Journal Entry (0..*)

---

## Area

contains

- Project (0..*)

---

## Meeting

supports

- Project (0..1)

references

- Reference (0..*)
- Resource (0..*)

---

## Reference

supports

- Project (0..*)
- Resource (0..*)

---

## Resource

supports

- Project (0..*)

references

- Reference (0..*)

---

## Journal Entry

references

- Project (0..*)
- Area (0..*)
- Resource (0..*)

---

# Relationship Overview

```text
Project
    belongs to → Area (0..1)
    contains → Meeting (0..*)
    references → Reference (0..*)
    references → Resource (0..*)
    references → Journal Entry (0..*)

Area
    contains → Project (0..*)

Meeting
    supports → Project (0..1)
    references → Reference (0..*)
    references → Resource (0..*)

Reference
    supports → Project (0..*)
    supports → Resource (0..*)

Resource
    supports → Project (0..*)
    references → Reference (0..*)

Journal Entry
    references → Project (0..*)
    references → Area (0..*)
    references → Resource (0..*)
```

The overview summarizes the canonical relationships defined by the
Interaction Model.

Detailed object-specific relationship contracts remain defined by the
individual Interaction Model documents.

---

# Relationship Semantics and Inverses

Some relationships describe complementary perspectives over the same
domain structure.

For example:

```text
Project
    belongs to → Area (0..1)

Area
    contains → Project (0..*)
```

These relationships are semantically complementary.

However, the Interaction Model does not require every relationship to
have an explicitly defined inverse.

For example:

```text
Project
    references → Resource
```

does not require:

```text
Resource
    referenced by → Project
```

to exist as a separate relationship type.

Relationships are introduced only when they express useful domain
semantics.

---

# Cardinality Semantics

The Interaction Model uses the following cardinality notation:

```text
0..1
```

Zero or one related object.

```text
0..*
```

Zero or more related objects.

Cardinality describes the multiplicity allowed by the semantic
relationship.

For example:

```text
Meeting
    supports
Project (0..1)
```

means that a Meeting may support no Project or one Project.

It does not imply that every Meeting must support a Project.

Likewise:

```text
Project
    references
Resource (0..*)
```

means that a Project may reference any number of Resources, including
none.

Cardinality must not be interpreted as an implementation-specific
storage constraint.

An implementation may enforce these contracts through files, metadata,
database constraints, validation, or another mechanism while preserving
the same domain semantics.

---

# Boundaries

The Interaction Model owns:

```text
Domain Object
      │
      │ semantic relationship
      ▼
Domain Object
```

including, when semantically relevant:

```text
relationship type
relationship direction
relationship cardinality
```

It does not own transformations between system states.

Those belong to the Workflow Model.

It does not own historical evidence of change.

That belongs to the Event Model.

It does not define the Domain Objects themselves or their lifecycles.

Those belong to the Domain Model.

---

# Interaction Model and Domain Model

The Domain Model answers:

> What exists in Ohtli, and what does it mean?

The Interaction Model answers:

> How are those Domain Objects related?

Conceptually:

```text
Domain Model
    │
    ├── Project
    ├── Area
    ├── Meeting
    ├── Reference
    ├── Resource
    └── Journal Entry

Interaction Model
    │
    └── semantic relationships between those objects
```

The Interaction Model therefore depends conceptually on the existence
and meaning of Domain Objects without redefining them.

---

# Interaction Model and Event Model

The Interaction Model describes semantic relationships.

The Event Model describes historical evidence of observable change.

For example:

```text
Project
    belongs to
Area
```

is a semantic relationship.

A historical fact indicating that a Project became associated with an
Area would belong to the Event Model if that change is represented as an
Event.

The relationship itself is not an Event.

---

# Interaction Model and Workflow Model

The Interaction Model defines semantic structure.

The Workflow Model defines transformations over relevant System State.

A workflow may establish, modify, or use relationships according to its
workflow contract.

However, relationships do not invoke workflows.

Likewise, the Interaction Model does not define how relationships are
created, modified, reviewed, or archived.

Those transformations belong to the corresponding workflow semantics.

---

# Scope

The Interaction Model defines:

- semantic relationships between Domain Objects;
- relationship types;
- relationship direction;
- relationship cardinality when multiplicity is part of the semantic
  contract.

The following concepts are intentionally excluded:

- behavioral business rules;
- Object lifecycles;
- Workflows;
- Events;
- workflow applicability;
- execution mechanisms;
- persistence mechanisms;
- filesystem representation;
- metadata representation;
- database schemas;
- implementation details.

These belong to other architectural models or later implementation
layers.

---

# Canonical Contracts

This README is the canonical entry point for the Ohtli Interaction
Model.

The detailed relationship contracts are defined by the individual
Domain Object interaction documents in this directory.

Those documents refine the relationships summarized here without
redefining the scope or architectural principles of the Interaction
Model.

Documents outside the Interaction Model may reference these
relationships but must not redefine their semantics or cardinality.

---

# Summary

The Ohtli Interaction Model defines how Domain Objects are semantically
related.

Its relationships are:

```text
belongs to
contains
references
supports
```

Relationships are directional and technology-independent.

Cardinality is included when multiplicity forms part of the semantic
relationship contract.

The canonical relationship structure is:

```text
Project
    belongs to → Area (0..1)
    contains → Meeting (0..*)
    references → Reference (0..*)
    references → Resource (0..*)
    references → Journal Entry (0..*)

Area
    contains → Project (0..*)

Meeting
    supports → Project (0..1)
    references → Reference (0..*)
    references → Resource (0..*)

Reference
    supports → Project (0..*)
    supports → Resource (0..*)

Resource
    supports → Project (0..*)
    references → Reference (0..*)

Journal Entry
    references → Project (0..*)
    references → Area (0..*)
    references → Resource (0..*)
```

The Interaction Model defines semantic structure between Domain Objects.

It does not define workflows, events, lifecycle transitions, behavioral
business rules, or implementation mechanisms.
