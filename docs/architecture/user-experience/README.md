# User Experience Model

## Status

Defined

## Purpose

The User Experience Model defines how the concepts established by Ohtli's
canonical models and Representation Model become understandable and
interactable by actors.

Its purpose is to provide a coherent experience of represented Domain Objects
while preserving the semantics and invariants established by the preceding
architectural models.

The User Experience Model does not introduce new domain semantics.

It establishes the canonical experience of:

- objects;
- current state;
- historical evidence;
- relationships;
- workflows;
- workflow results;
- lifecycle continuity.

## Scope

The User Experience Model consolidates the following experience contracts:

- UX foundations;
- object-centered experience;
- state and history experience;
- relationship experience;
- workflow interaction experience.

These contracts are defined in the corresponding documents within this
directory.

The User Experience Model is concerned with conceptual experience and
interaction semantics.

It does not define implementation technology.

## Architectural Position

The User Experience Model is downstream from the canonical models in terms of
semantic authority.

Conceptually:

```text
Phase 3 — Canonical Models
│
├── Domain Model
├── Interaction Model
├── Event Model
└── Workflow Model
        │
        ▼
Phase 4 — Representation Model
        │
        ▼
Phase 5 — User Experience Model
```

This relationship represents conceptual and semantic authority.

It does not prescribe an implementation architecture, runtime pipeline, data
flow, or technology stack.

The User Experience Model consumes the concepts and representations established
by the preceding models without redefining them.

## Primary Unit of Experience

The represented Domain Object is the primary unit of experience.

The object provides the context within which users understand:

```text
Object
│
├── Current State
├── Relationships
├── History
└── Workflows
```

The object remains identifiable throughout its lifecycle.

Experience must preserve the distinction between:

```text
Object Identity
        ≠
Object Representation
```

A change in representation, location, name, lifecycle status, or other
contextual property must not silently imply the creation of a different object.

## Object-Centered Experience

The experience is organized around the represented object and its context.

Users should be able to understand an object's relevant information without
having to reconstruct that information from low-level system mechanisms.

The object-centered experience provides access to:

- current state;
- relationships;
- historical evidence;
- workflows;
- workflow results;
- relevant contextual information.

The object is therefore the stable contextual anchor for interaction.

## State and History Experience

Current State must be directly understandable.

The experience must not require:

```text
Events
  ↓
Replay
  ↓
Current State
```

as the only mechanism for understanding the current condition of an object.

The experience preserves:

```text
Current State
      ≠
Historical Evidence
```

Historical information may explain how an object reached its current condition,
but historical presence does not imply current state.

Likewise:

```text
Historical Evidence
      ≠
Current State
```

Historical information remains accessible without silently becoming a statement
about the present.

### Authoritative and Derived State

The experience must preserve the distinction between authoritative and derived
state.

```text
Authoritative State
      ≠
Derived State
```

Derived information may provide useful contextual information, but it must not
silently appear to be authoritative state.

The UX exposes the distinction without redefining the underlying state model.

### Lifecycle Continuity

Lifecycle changes do not create a new identity unless the canonical Domain Model
defines such a semantic change.

In particular:

```text
Archive
   ↓
same identity

Reactivate
   ↓
same identity
```

The experience must not represent reactivation as the creation of a new object.

Identity continuity remains stable across:

- rename;
- relocation;
- archive;
- reactivation;
- other lifecycle changes defined by the canonical models.

## Relationship Experience

Relationships are experienced as part of the object's contextual workspace.

Conceptually:

```text
Object
│
├── State
├── Relationships
│   │
│   ├── Related Object A
│   ├── Related Object B
│   └── ...
├── History
└── Workflows
```

The User Experience Model preserves the canonical relationship semantics
established by the Interaction Model.

The following remain authoritative:

- relationship meaning;
- direction;
- cardinality;
- stable identity.

A visual or navigational representation must not redefine relationship
semantics.

Therefore:

```text
Relationship Semantics
      ≠
Visual Presentation
```

When moving from one object to a related object, enough contextual information
should remain available for the actor to understand the relationship that
caused the transition.

## Workflow Interaction Experience

Workflows are experienced within the context of the represented object.

The experience preserves:

```text
Applicability
      ≠
Capability
      ≠
Authority
      ≠
Execution
```

Applicability is determined by the Workflow Model.

The UX exposes applicability without redefining workflow preconditions.

### Discovery

Workflow discovery does not imply execution.

A workflow may be discovered because it is:

- applicable;
- potentially relevant;
- recommended;
- historically relevant.

Therefore:

```text
Discovery
      ≠
Applicability
      ≠
Execution
```

### Applicability and Availability

The experience distinguishes:

```text
Applicable
      ≠
Available
```

A workflow may be applicable without being currently available for interaction.

Availability must not be interpreted as authority or authorization.

### Execution

Execution is an explicit interaction.

Conceptually:

```text
Applicable
      ↓
Available
      ↓
Execution Requested
      ↓
[Confirmation when applicable]
      ↓
Execution
      ↓
Outcome
```

A workflow is not considered executed merely because it is:

- visible;
- discovered;
- applicable;
- available;
- recommended;
- inspected.

Confirmation, when present, remains distinct from execution.

### Results

A workflow execution produces an outcome that remains distinguishable from
current state.

```text
Execution
      ↓
Result
```

Therefore:

```text
Result
      ≠
Current State
```

A result may provide useful information without changing represented state.

### Non-Persistent Results

A workflow may produce a result that does not become persistent represented
state.

Such results remain associated with their execution context.

```text
Execution
      ↓
Non-Persistent Result
```

The UX must not silently promote a non-persistent result into authoritative
state.

### State Transformation

When workflow execution transforms represented state:

```text
Execution
      ↓
Transformation
      ↓
Updated State
      ↓
Current State
```

The resulting representation must continue to satisfy Representation Model
invariants.

The UX communicates the transformation and its result but does not redefine
the transformation semantics.

### Execution and State Change

Workflow execution and state change remain distinct.

```text
Workflow Execution
      ≠
State Change
```

An execution may produce a result without changing state.

Alternatively:

```text
Execution
      ↓
Transformation
      ↓
State Change
```

The existence of an execution must therefore not imply that a state change
occurred.

### Historical Workflow Experience

Historical execution remains distinguishable from current applicability.

For example:

```text
Previous State:
Pending

Approve:
Applicable
```

After execution:

```text
Current State:
Approved

Approve:
Not Applicable
```

Historical evidence may still show:

```text
Approve:
Executed Successfully
```

These statements describe different contexts and are not contradictory.

## Recommendations

Recommendations may assist workflow discovery and contextual understanding.

They remain distinct from workflow semantics:

```text
Recommendation
      ≠
Applicability
      ≠
Availability
      ≠
Execution
```

A recommendation may refer to a workflow that is currently non-applicable.

For example:

```text
Recommended next step:
Close invoice

Currently not applicable.

Reason:
The invoice must be approved first.
```

A recommendation does not imply that a workflow is executable.

Recommendation reasons are contextual explanations and remain distinct from
canonical applicability conditions:

```text
Recommendation Reason
      ≠
Applicability Conditions
```

Recommendations do not define:

- workflow semantics;
- applicability rules;
- ranking algorithms;
- recommendation engines;
- AI recommendation architectures.

## Cross-Model Consistency

The complete User Experience Model must remain consistent with the preceding
architectural models.

### Domain Model

The UX preserves:

- Domain Object identity;
- Domain Object semantics;
- lifecycle semantics.

The UX must not redefine what constitutes a Domain Object.

### Interaction Model

The UX preserves:

- relationship meaning;
- direction;
- cardinality;
- stable identity.

The UX must not introduce new relationship types or cardinality rules.

### Event Model

The UX distinguishes:

```text
Current State
      ≠
Historical Evidence
```

Current State must remain directly understandable without requiring Event
reconstruction.

Events may provide historical evidence, but the UX must not require Event
replay as the sole mechanism for understanding current state.

### Workflow Model

The UX preserves:

- workflow preconditions;
- applicability;
- execution;
- transformation;
- results.

The following distinctions remain explicit:

```text
Applicability
      ≠
Execution
```

```text
Applicability
      ≠
Capability
```

```text
Applicability
      ≠
Authority
```

```text
Workflow Execution
      ≠
State Change
```

```text
Workflow Result
      ≠
Current State
```

The UX does not redefine workflow semantics.

### Representation Model

The UX consumes workflow-facing and object-facing representations without
redefining:

- identity;
- state;
- relationships;
- Events;
- workflow-facing representation;
- representation invariants.

The Representation Model remains authoritative for representation semantics.

## Identity Continuity

Identity remains continuous across historical and lifecycle changes unless the
canonical Domain Model explicitly defines otherwise.

The UX must preserve identity across:

```text
Rename
   ↓
same object

Relocation
   ↓
same object

Archive
   ↓
same object

Reactivate
   ↓
same object
```

Historical changes may alter the object's state or representation without
creating an implied new identity.

## Actor Independence

The User Experience Model is independent of the type of actor interacting with
the system.

The same conceptual experience must support:

```text
Human
System
AI-Assisted
Hybrid
```

Actor differences may affect how an interaction is performed, but they do not
change the underlying UX semantics.

Therefore:

```text
Actor
      ≠
Workflow Semantics
```

and:

```text
Actor
      ≠
Domain Semantics
```

## AI Optionality

AI is optional.

The User Experience Model must remain complete and meaningful without AI.

AI-assisted interaction may support activities such as:

- discovery;
- explanation;
- recommendation;
- interaction assistance.

AI does not become authoritative for:

- Domain Object identity;
- relationship semantics;
- current state;
- workflow applicability;
- workflow execution semantics;
- transformation semantics.

Therefore:

```text
AI
      ≠
Semantic Authority
```

The UX must remain valid when no AI capability is present.

## Technology Independence

The User Experience Model is conceptually independent of implementation
technology.

The following are implementation possibilities, not UX architectural concepts:

```text
Markdown
YAML
Filesystem
Database
Obsidian
Web Framework
Desktop Framework
Mobile Framework
API
AI Provider
```

Therefore:

```text
User Experience Model
      ≠
Implementation Technology
```

A future implementation may use any combination of these technologies without
changing the conceptual UX model.

The UX does not define:

- frontend frameworks;
- backend architectures;
- APIs;
- database schemas;
- filesystem layouts;
- storage mechanisms;
- UI component systems.

## Canonical UX Principles

The User Experience Model is governed by the following principles:

1. The represented Domain Object is the primary unit of experience.
2. Object identity remains continuous across applicable lifecycle changes.
3. Current State is directly understandable.
4. Current State remains distinct from Historical Evidence.
5. Authoritative State remains distinct from Derived State.
6. Relationship meaning, direction, cardinality, and identity are preserved.
7. Workflow applicability remains distinct from capability, authority, and
   execution.
8. Workflow execution remains distinct from state change.
9. Workflow results remain distinct from Current State.
10. Historical workflow information remains distinguishable from current
    applicability.
11. Different actors may interact with the same conceptual UX.
12. AI remains optional.
13. The UX does not acquire semantic authority from implementation technology.
14. Representation is consumed without redefining Representation Model
    semantics.
15. Current State does not depend on Event reconstruction as its only
    experiential representation.

## Architectural Boundaries

The User Experience Model must not define:

- UI implementation;
- visual design systems;
- frontend frameworks;
- backend architecture;
- APIs;
- database schemas;
- filesystem layouts;
- workflow engines;
- schedulers;
- automation;
- agents;
- authorization systems;
- orchestration frameworks;
- AI providers;
- new Domain Objects;
- new relationship types;
- new workflow types;
- new workflow semantics;
- new applicability rules;
- new transformation semantics.

The canonical models remain authoritative.

The User Experience Model defines how those semantics are experienced, not how
they are implemented.

## Future Implementation Phases

Future implementation phases may translate the User Experience Model into
concrete interfaces, interaction mechanisms, and technologies.

Such implementations may use:

- web applications;
- desktop applications;
- mobile applications;
- command-line interfaces;
- Markdown-based environments;
- databases;
- APIs;
- AI-assisted interfaces;
- other technologies.

Those implementation choices must preserve the conceptual contracts established
by the User Experience Model.

Implementation must therefore proceed from the model rather than redefining the
model.

## Consolidated Experience

The complete conceptual experience can be summarized as:

```text
                         Domain Object
                              |
                              v
                       Object Context
                              |
              +---------------+---------------+
              |               |               |
              v               v               v
          State        Relationships       History
              |               |               |
              |               |               |
              +---------------+---------------+
                              |
                              v
                         Workflows
                              |
                +-------------+-------------+
                |                           |
                v                           v
         Recommendation               Applicability
                |                           |
                |                      Availability
                |                           |
                +-------------+-------------+
                              |
                              v
                     Execution Requested
                              |
                              v
                    Confirmation
                    (when applicable)
                              |
                              v
                          Execution
                              |
                         +----+----+
                         |         |
                         v         v
                      Result   Transformation
                                   |
                                   v
                             Updated State
                                   |
                                   v
                             Current State
```

Historical evidence remains accessible throughout the experience without
becoming current state:

```text
Historical Evidence
        ≠
Current State
```

The complete User Experience Model therefore provides a coherent object-centered
experience while preserving the semantic authority and boundaries of the
Domain, Interaction, Event, Workflow, and Representation Models.

## Canonical Entry Point

This document is the canonical entry point for Phase 5 — User Experience Model.

The detailed experience contracts remain in the corresponding documents in
this directory.

The README consolidates their relationships and establishes the common
architectural principles and boundaries for future implementation.
