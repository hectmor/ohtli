# Workflow-Facing Representation

## Purpose

The Workflow-Facing Representation defines how workflows inspect and transform
relevant represented Ohtli state without redefining Workflow semantics or
introducing workflow execution technology.

It establishes the representation boundary between the Representation Model
and the Workflow Model.

The Workflow Model remains authoritative for workflow semantics, including
preconditions, applicability, and transformation semantics.

---

# Workflow-Facing Representation

A Workflow-Facing Representation is a workflow-specific projection of the
canonical Current Representation, potentially incorporating explicitly
authorized Relevant Context.

```text
Canonical Current Representation
             │
             ├── represented facts
             │
             └── authorized Relevant Context
                       │
                       ▼
          Workflow-Facing Representation
                       │
                       ▼
                  Workflow Model
```

It is not a second canonical representation.

```text
Workflow-Facing Representation
    ≠
Canonical Current Representation
```

---

# Relevant Context

A Workflow may require information that is relevant to applicability or
transformation but is not persistent represented state.

The Workflow-Facing Representation may combine:

```text
Represented State
        +
Relevant Context
        │
        ▼
Workflow-Facing Representation
```

Relevant Context may include:

- current time;
- execution context;
- temporary inputs;
- external conditions;
- explicitly authorized derived environmental information.

Relevant Context does not automatically become persistent Ohtli state.

```text
Relevant Context
    ≠ Represented State

Relevant Context
    ≠ Persistent Domain State
```

---

# Preconditions and Applicability

Workflow preconditions are defined and evaluated by the Workflow Model.

The Workflow-Facing Representation exposes the facts required for that
evaluation.

```text
Workflow-Facing Representation
             │
             ▼
Workflow Preconditions
             │
             ▼
Applicable / Not Applicable
```

The Representation Model does not evaluate Workflow preconditions.

Therefore:

```text
Representation
    → exposes facts

Workflow Model
    → defines and evaluates preconditions
```

Applicability does not imply execution, capability, or authority.

```text
Applicability
    ≠ Execution

Applicability
    ≠ Capability

Applicability
    ≠ Authority
```

---

# Inspectable and Transformable State

A Workflow may inspect represented information exposed through its
Workflow-Facing Representation.

Inspection does not imply transformation rights.

```text
Inspectable
    ≠ Transformable
```

A Workflow may transform only represented elements explicitly permitted by its
canonical Workflow contract.

```text
Workflow-Facing Representation
             │
             ▼
        Workflow Contract
             │
             ├── inspectable elements
             │
             └── transformable elements
                         │
                         ▼
                   Transformation
```

The Workflow Model remains authoritative for transformation semantics.

---

# Transformation Results

A Workflow transformation produces a Transformation Result.

```text
Workflow
    │
    ▼
Transformation Result
```

A Transformation Result is not automatically persistent.

```text
Transformation Result
    ≠ Represented State

Transformation Result
    ≠ Domain Object

Transformation Result
    ≠ Current Representation
```

A Workflow may produce persistent or non-persistent results.

```text
Workflow Result
    │
    ├── Persistent Result
    │       │
    │       ▼
    │   Current Representation
    │
    └── Non-Persistent Result
            │
            ▼
        Workflow Context
```

Only a result explicitly defined as representational by the applicable
canonical contract may update the Current Representation.

```text
Non-Persistent Result
    ≠ Missing Representation
```

---

# Updating Current Representation

A Workflow transformation may update the Current Representation only when its
result is explicitly representational and accepted by the applicable
canonical contracts.

```text
Workflow
    │
    ▼
Transformation Result
    │
    ▼
Representation Contracts
    │
    ├── valid ──→ Current Representation
    │
    └── invalid → rejected
```

Representation invariants remain the responsibility of the Representation
Model.

```text
Workflow
    → Transformation Semantics

Representation
    → Representation Invariants
```

---

# Workflow and State

A Workflow may inspect and transform represented State only according to the
applicable Workflow and State contracts.

The Workflow-Facing Representation does not redefine State semantics.

---

# Workflow and Relationships

A Workflow may inspect or transform relationships only as permitted by its
canonical Workflow contract.

Relationship semantics remain owned by the Interaction Model.

The Workflow Model does not redefine:

- Relationship Types;
- relationship meaning;
- cardinality;
- uniqueness.

---

# Workflow and Events

A Workflow transformation may result in a change to represented state.

Historical occurrence of that change belongs to the Event Model.

```text
Workflow
    │
    ▼
Transformation
    │
    ▼
Current Representation
    │
    ▼
Historical Event
```

The Workflow-Facing Representation does not define historical semantics.

---

# Workflow and Projections

The Workflow-Facing Representation is a specialized Projection of the
canonical Current Representation.

It does not become:

- a second Current Representation;
- a Domain Object;
- a View;
- a Workflow Engine;
- an authorization system.

```text
Canonical Current Representation
             │
             ▼
Workflow-Facing Projection
             │
             ▼
Workflow
```

A Workflow-Facing Projection and a presentation Projection serve different
purposes.

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

# Actor Independence

The same Workflow-Facing Representation contract must remain usable by:

```text
Human
Deterministic System
AI-Assisted System
Hybrid System
```

The actor or execution mechanism does not change the representation contract.

AI is optional and has no special architectural authority.

This document does not define execution technology.

---

# Future Workflow Applicability

A valid persistent transformation may change the Current Representation.

That updated representation may change the result of future Workflow
precondition evaluation.

```text
Workflow A
    │
    ▼
Transformation
    │
    ▼
Updated Current Representation
    │
    ▼
Workflow B Preconditions
    │
    ▼
Applicable / Not Applicable
```

Representation provides current facts; the Workflow Model remains responsible
for applicability semantics.

---

# Architectural Boundary

```text
Canonical Current Representation
             │
             ├── represented state
             ├── relationships
             └── authorized Relevant Context
                         │
                         ▼
            Workflow-Facing Representation
                         │
                         ▼
                Workflow Preconditions
                         │
                         ▼
                Applicable / Not Applicable
                         │
                         │ if executed
                         ▼
                  Transformation
                         │
                         ▼
                Transformation Result
                    /           \
                   /             \
                  ▼               ▼
          Persistent Result   Non-Persistent Result
                  │               │
                  ▼               ▼
       Representation         Workflow Context
          Validation
                  │
                  ▼
       Canonical Current Representation
```

The execution mechanism is deliberately outside this boundary.

---

# Invariants

## Observation

- Workflow-Facing Representation is a specialized projection.
- It may expose relevant represented state.
- It may include explicitly authorized Relevant Context.
- Inspection does not imply transformation authority.

## Applicability

- Workflow preconditions are defined by the Workflow Model.
- Workflow preconditions are evaluated against Workflow-Facing Representation.
- Applicability does not imply execution.
- Applicability does not imply capability.
- Applicability does not imply authority.

## Transformation

- A Workflow transforms only elements permitted by its canonical contract.
- Transformation semantics belong to the Workflow Model.
- Transformation Result is not automatically persistent.
- Only explicitly representational results may update Current Representation.

## Representation Integrity

- Transformation results must satisfy applicable canonical contracts.
- Representation invariants are not redefined by workflows.
- Invalid transformation results do not update Current Representation.

## Context

- Relevant Context may participate in Workflow evaluation.
- Relevant Context does not automatically become persistent represented state.
- Context semantics remain governed by applicable canonical contracts.

## Persistence

- Persistent Workflow Results may update Current Representation after
  validation.
- Non-persistent Workflow Results do not automatically update Current
  Representation.
- Non-persistent results are not equivalent to missing representation.

## Actor Independence

- The representation contract is actor-independent.
- Humans, deterministic systems, AI-assisted systems, and hybrid systems may
  use the same contract.
- AI is optional.
- Actor capability or authority is not defined by the Representation Model.

---

# Scope

This document defines:

- the Workflow-Facing Representation boundary;
- workflow-relevant represented state;
- Relevant Context;
- workflow precondition inspection;
- inspectable and transformable representation;
- Transformation Results;
- persistent and non-persistent results;
- representation validation after transformation;
- future applicability through updated representation;
- actor independence.

It does not define:

- workflow engines;
- schedulers;
- agents;
- LLM providers;
- authorization systems;
- orchestration frameworks;
- APIs;
- automation policies;
- execution technology;
- Workflow Model semantics that belong to the Workflow Model.
