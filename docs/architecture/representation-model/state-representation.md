# State Representation

## Purpose

The State Representation defines how the current represented state of an
Ohtli Represented Instance is structured and interpreted.

It refines the Representation Foundations without redefining the canonical
semantics established by the Domain, Interaction, Event, and Workflow Models.

It answers:

> What current state is represented for an architectural instance, and how is
> that state distinguished from derived information, representation
> conditions, transitions, and historical evidence?

---

# Represented State

Represented State is the set of represented facts currently applicable to a
Represented Instance according to its applicable architectural contracts.

A Represented Instance therefore has the conceptual form:

```text
Represented Instance
│
├── Representation Core
│   ├── Identity
│   └── Architectural Type
│
└── Represented State
```

Represented State is technology independent.

It does not prescribe Markdown fields, YAML properties, database columns,
programming-language attributes, serialization formats, or storage schemas.

---

# Authoritative and Derived State

Represented State is divided into:

```text
Represented State
├── Authoritative State
└── Derived State
```

## Authoritative State

Authoritative State contains the canonical currently represented facts for the
applicable architectural contracts. These facts are not derived from other
represented information.

## Derived State

Derived State contains represented facts determined from architecturally valid
inputs such as authoritative state, relationships, Events, relevant context,
time, or other explicitly permitted represented information.

Derived State is determined, not independently asserted.

```text
Authoritative Inputs
        │
        ▼
    Derivation
        │
        ▼
  Derived State
```

A derived value may be materialized or cached without becoming authoritative.

Therefore:

```text
Authoritative ≠ Persistent
Derived ≠ Transient
Derived ≠ Unstored
```

---

# State Dimensions

A State Dimension is an architecturally defined aspect of Represented State
that has its own state domain and an explicit contract governing the evolution
of its current state.

A State Dimension exists only when the canonical architecture defines it.

The Representation Model does not invent State Dimensions.

```text
Canonical Architecture
        │
        ▼
State Dimension Contract
        │
        ▼
Representation
```

Examples already defined by the canonical architecture include:

- Lifecycle
- Contextual Presence

Title, Description, Creation Time, and similar information do not become State
Dimensions merely because their values may change.

---

# State Dimension Contract

The contract governing a State Dimension belongs to the applicable canonical
architectural model.

It may define:

- valid state values;
- valid transitions;
- invariants;
- transition constraints;
- other semantic rules.

The Representation Model represents these contracts but does not redefine
them or create a second model for Lifecycle, Presence, or any other canonical
concept.

```text
State Dimension
├── Applicable Architectural Contract
│   ├── Valid Values
│   └── Valid Transitions
└── Current State Value
```

---

# Current State Value

A Represented Instance contains the current value of each applicable State
Dimension.

For example:

```text
Project α

Lifecycle
    Current Value = Active

Contextual Presence
    Current Value = Operational
```

The State Dimension is the governed aspect of state. The Current State Value
is its current condition.

```text
State Dimension ≠ State Value
```

---

# State Values

Authoritative State may also contain values that do not constitute
independently evolving State Dimensions.

Examples include:

- Title
- Description
- Creation Time
- other authoritative information defined by applicable contracts

A State Value is current authoritative information whose value does not
constitute an independently evolving State Dimension.

A State Value may have validation constraints without having an independent
state-evolution contract.

```text
State Value ≠ State Dimension
```

---

# State Transitions

A State Transition is a valid change from one State Value to another within a
State Dimension.

```text
Lifecycle

Active
   │
   │ valid transition
   ▼
Completed
```

The transition must satisfy the applicable architectural contract of that
State Dimension.

The transition itself is not part of current represented state. After the
transition, the representation contains the new current value.

```text
State Transition ≠ Current State Value
```

---

# State Transition and Workflow

A State Transition and a Workflow are different concepts.

The Representation Model represents the state change and the constraints
defined by the applicable architectural contract.

The Workflow Model determines workflow applicability and execution.

```text
Workflow
    │
    ▼
State Transition
    │
    ▼
Current State
```

The Representation Model does not define when a Workflow may execute, and the
Workflow Model does not redefine the meaning of a State Dimension.

---

# Lifecycle and Contextual Presence

Lifecycle and Contextual Presence are independent State Dimensions when
defined by the applicable canonical architectural contracts.

For example:

```text
Project α

Lifecycle
    Completed

Contextual Presence
    Operational
```

Archive may transform:

```text
Contextual Presence:
Operational → Historical
```

without changing:

```text
Lifecycle:
Completed
```

The resulting state may therefore be:

```text
Lifecycle
    Completed

Contextual Presence
    Historical
```

This preserves:

```text
Lifecycle ≠ Contextual Presence
```

and does not imply that Archive completes a Project.

---

# Representation Conditions

A Representation Condition describes the condition of the representation of a
state value or dimension.

Representation Conditions are not State Values.

```text
Representation Condition
├── Known
├── Unknown
├── Missing
├── Not Applicable
└── Invalid
```

These conditions must not be added to the semantic state domain of a State
Dimension.

For example, a Lifecycle domain may contain:

```text
Created
Active
On Hold
Completed
```

but not Unknown, Missing, Invalid, or Not Applicable.

---

# Known

Known indicates that the applicable current state value is represented and
known.

```text
Lifecycle
    Current Value = Active
    Condition = Known
```

Known is a representation condition, not a Lifecycle value.

---

# Unknown

Unknown indicates that the dimension applies and has a current conceptual
value, but that value is not currently known.

```text
Lifecycle
    Current Value = ?
    Condition = Unknown
```

Unknown does not mean invalid, failure, success, not applicable, or a default
value.

Its consequences are contextual. A consuming architectural contract
determines whether an unknown value satisfies its preconditions.

For example, a workflow requiring `Lifecycle = Active` cannot establish that
precondition from Unknown. A Processing workflow whose purpose is to determine
Lifecycle may instead accept Unknown as its starting condition.

```text
Unknown ≠ Invalid
Unknown ≠ Failure
```

---

# Missing

Missing indicates that a dimension applies and the representation is expected
to contain its current value, but the value is absent.

```text
Lifecycle
    Current Value = absent
    Condition = Missing
```

Missing is a condition of representation completeness, not a State Value.

```text
Unknown
    → value is not currently known

Missing
    → expected representation is absent
```

---

# Not Applicable

Not Applicable indicates that a particular State Dimension does not apply to
the represented Architectural Type or applicable architectural context.

It is not a value in the domain of that State Dimension.

```text
Lifecycle
    Condition = Not Applicable
```

does not add `Not Applicable` to the Lifecycle state domain.

---

# Invalid

Invalid indicates that the representation contains a value that violates the
applicable contract.

```text
Lifecycle
    Current Value = "Banana"
    Condition = Invalid
```

Invalid does not become a Lifecycle value and cannot redefine the valid domain.

---

# Unknown and Workflow Preconditions

Unknown does not have a universal operational meaning.

The Representation Model records the uncertainty. The consuming contract
determines whether that uncertainty satisfies its requirements.

```text
Represented State
        │
        ▼
Representation Condition = Unknown
        │
        ▼
Consuming Contract
        │
        ├── sufficient
        └── insufficient
```

This prevents Representation Model from embedding workflow-specific decisions.

---

# Current State and History

The Representation Model represents current state.

Historical changes are represented independently through the Event Model or
other architecturally defined historical evidence.

```text
Representation Model
        │
        ▼
Current State

Event Model
        │
        ▼
Historical Occurrences
```

The Representation Model does not require current state to contain its
complete history.

It does not require Event Sourcing or any specific mechanism for reconstructing
current state from historical Events.

Therefore:

```text
Current State ≠ History
State Transition ≠ Event
Event ≠ Current State
```

A State Transition may be associated with or evidenced by an Event, but the
concepts remain distinct.

---

# Derived State and History

Derived State does not constitute historical evidence.

For example:

```text
Current Authoritative State
    Lifecycle = Completed

Derived State
    is_active = false
```

is different from:

```text
Historical Event
    ProjectCompleted
```

Derived State describes what can currently be determined. Historical evidence
describes what occurred.

---

# State Representation and Relationships

Relationships defined by the Interaction Model are not automatically State
Dimensions.

For example:

```text
Project α
    belongs to
Area β
```

remains an Interaction Model relationship.

It must not be converted into a State Dimension merely because the relationship
may change.

The Interaction Model retains authority over semantic relationships.

---

# State Representation and Workflow Model

The Representation Model provides the state that workflows observe and may
transform.

The Workflow Model defines workflow semantics, applicability, preconditions,
execution, workflow outputs, and workflow-specific transformation rules.

The Representation Model defines how resulting current state is represented.

```text
Representation Model
    → represents state

Workflow Model
    → acts on state

Event Model
    → represents historical occurrence
```

No model should silently assume the responsibilities of another.

---

# State Representation and Event Model

A state change may produce or be evidenced by an Event.

For example:

```text
Lifecycle
    Active → Completed
```

may be associated with:

```text
ProjectCompleted
```

However:

```text
State Transition ≠ Event
```

The Event Model defines Event semantics, identity, provenance, and historical
meaning.

The Representation Model defines the resulting current state.

---

# Derived State Is Not Authoritative

A materialized or cached derived value does not become authoritative merely
because it is stored.

For example:

```text
Authoritative:
    Resources = {A, B, C}

Derived:
    resource_count = 3
```

An implementation may persist `resource_count`. It remains derived because:

```text
resource_count = f(Resources)
```

If the materialized value conflicts with authoritative inputs, authoritative
inputs retain authority and the derived value must be recomputed or treated as
stale/invalid according to the applicable implementation contract.

---

# State Representation Invariants

## Representation

- Represented State contains currently applicable represented facts.
- Represented State is technology independent.
- Representation does not redefine canonical architectural semantics.

## Authority

- Authoritative State contains canonical currently represented facts.
- Derived State is determined rather than independently asserted.
- Persistence does not make a fact authoritative.
- Derived information may be materialized or cached.

## State Dimensions

- A State Dimension exists only when defined by canonical architecture.
- A State Dimension has an applicable architectural contract.
- The contract defines its valid state domain and evolution rules.
- Representation does not independently redefine the contract.
- Lifecycle and Contextual Presence remain independent dimensions when defined
  by the canonical architecture.

## Values and Transitions

- A State Value is not automatically a State Dimension.
- A State Transition changes the current value of a State Dimension.
- A State Transition must satisfy the applicable architectural contract.
- A State Transition is not itself current state.
- A State Transition is not an Event.

## Representation Conditions

- Representation Conditions are not State Values.
- Unknown is not Invalid.
- Unknown is not Failure.
- Missing is distinct from Unknown.
- Not Applicable does not expand a State Dimension's domain.
- Invalid does not expand a State Dimension's domain.

## History

- Current State is distinct from historical evidence.
- The Representation Model does not require Event Sourcing.
- Historical evidence is governed by the Event Model or another canonical
  historical mechanism.

## Architectural Boundaries

- Relationships remain governed by the Interaction Model.
- Workflow applicability remains governed by the Workflow Model.
- Event semantics remain governed by the Event Model.
- Representation Model does not introduce new domain semantics.

---

# Conceptual Example

A Project may be represented as:

```text
Project α

Representation Core
├── Identity = α
└── Architectural Type = Project

Represented State
│
├── Authoritative State
│   │
│   ├── Lifecycle
│   │     Current Value = Active
│   │
│   ├── Contextual Presence
│   │     Current Value = Operational
│   │
│   └── Title
│         Current Value = "Ohtli"
│
└── Derived State
      resource_count = 8
      is_active = true
```

A valid Execution transformation may produce:

```text
Lifecycle:
    Active → Completed
```

Result:

```text
Lifecycle
    Current Value = Completed

Contextual Presence
    Current Value = Operational
```

Archive may then produce:

```text
Contextual Presence:
    Operational → Historical
```

Result:

```text
Lifecycle
    Current Value = Completed

Contextual Presence
    Current Value = Historical
```

The identity and architectural type remain unchanged.

Historical Events remain outside the current state representation.

---

# Scope

This document defines the representation of current state.

It does not define:

- concrete storage schemas;
- serialization formats;
- filesystem layouts;
- user interfaces;
- implementation-specific caching;
- Event Sourcing;
- workflow implementation;
- new lifecycle semantics;
- new relationship semantics;
- new domain concepts.

Those concerns remain governed by the appropriate architectural models or
later implementation phases.

