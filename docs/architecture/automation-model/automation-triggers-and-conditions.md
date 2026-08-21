# Automation Triggers and Conditions

## Purpose

This contract defines how an Automation evaluates whether to produce an
Execution Request: what a Trigger is, what an Automation Condition is,
how they relate to Workflow Applicability, and what outcomes are
possible. It preserves the Workflow Model's applicability semantics and
the Event Model's historical semantics.

## Evaluation Sequence

```text
Trigger
    ↓
Automation Evaluation
    ↓
Automation Conditions
    ↓
Workflow Applicability
    ↓
Execution Request
    ↓
Workflow Execution
```

This sequence expresses conceptual dependency, not a mandatory runtime
pipeline, data flow, or implementation architecture.

## Trigger

A Trigger is a conceptual signal that an Automation responds to by
beginning evaluation. A Trigger occurring does not itself produce an
Execution or a state change.

```text
Trigger != Automation Condition
Trigger != Workflow Applicability
Trigger Occurrence != Execution
```

This model does not prescribe what may serve as a Trigger, nor a
taxonomy of trigger kinds. It intentionally does not define temporal
mechanisms, scheduling technology, or external signal infrastructure.

## Automation Condition

An Automation Condition is a constraint, specific to a particular
Automation, that must hold for evaluation to proceed toward Workflow
Applicability after a Trigger occurs.

```text
Automation Condition != Workflow Precondition
```

Automation Conditions are additional and automation-specific. They do
not replace, weaken, or substitute for Workflow preconditions. A
satisfied Automation Condition never overrides an unsatisfied Workflow
precondition, and Workflow Applicability remains solely determined by the
Workflow Model.

This model introduces no generic condition taxonomy or expression
language.

## Evaluation Outcomes

```text
Trigger
    ↓
Conditions fail
    ↓
No Execution Request
```

```text
Trigger
    ↓
Conditions pass
    ↓
Workflow not applicable
    ↓
No Execution Request
```

```text
Trigger
    ↓
Conditions pass
    ↓
Workflow applicable
    ↓
Execution Request
    ↓
Workflow Execution
    ↓
Execution Outcome
    ↓
Execution Result
```

A Trigger occurring does not guarantee an Execution Request. An Execution
Request does not guarantee a Workflow Execution occurs, nor that it
produces a state change.

```text
Automation != guarantee of Execution
Execution Request != guarantee of Workflow Execution
```

## Multiple Triggers

An Automation may respond to a Trigger occurring more than once. Each
occurrence is evaluated independently.

```text
Trigger Occurrence α  →  Evaluation α  →  Outcome α
Trigger Occurrence β  →  Evaluation β  →  Outcome β
```

A prior Trigger occurrence, evaluation, or Execution Request does not
determine the outcome of a subsequent one. This model does not define
concurrency, deduplication, debouncing, or ordering mechanisms among
Trigger occurrences.

## Automation and Event

Automation Triggers and Events have separate responsibilities.

| Concept | Meaning |
| --- | --- |
| Event | Immutable evidence of a completed observable fact affecting Domain Objects. |
| Trigger | A conceptual signal that begins Automation evaluation. |

```text
Trigger != Event
```

An Event, when the Event Model applies, may serve as one conceptual
source of a Trigger. Not every Trigger corresponds to an Event, and not
every Event is a Trigger. This model does not establish that every Event
must be observable as a Trigger, nor that every Automation must be
triggered by an Event.

## Automation and State

Automation does not modify state directly.

```text
Automation
    ↓
may initiate Execution Request
    ↓
Workflow Execution
    ↓
may produce Transformation
    ↓
Transformation may change State
```

```text
Automation != State Change
```

Any resulting state transformation remains governed by the Workflow
Model and must satisfy applicable Representation Invariants, exactly as
for a non-automated Execution.

## Automation History

Automation History is the historical association of an Automation with
its configuration changes, activation and suspension, Trigger
occurrences, evaluation outcomes, and any resulting Execution Requests
and Workflow Executions.

```text
Automation History != Event History
Automation History != Execution History
Automation History != Current Applicability
```

Not every internal Automation operation must become an Event. Automation
History may refer to Event evidence and to Execution History without
replacing either. Neither Event nor Automation replay is required to
understand Current State.

## Cross-Model Consistency

- **Domain Model:** Automation creates no Domain Object and changes
  neither identity nor lifecycle semantics.
- **Interaction Model:** Automation creates no relationship semantics.
- **Event Model:** Events remain immutable evidence; a Trigger is not an
  Event.
- **Workflow Model:** It remains authoritative for preconditions,
  applicability, transformations, and results.
- **Execution Model:** It remains authoritative for Execution Request,
  Workflow Execution, Actor participation, Execution Context, Outcome,
  Result, and Execution History.
- **Representation Model:** Any accepted transformation preserves all
  applicable representation invariants; independently represented
  Automation identity is stable.
- **User Experience Model:** Automation existing, being active, being
  triggered, an Execution occurring, and a state change remain
  distinguishable.

## Boundaries

This contract does not define trigger taxonomies, condition expression
languages, scheduling technology, event sourcing, concurrency or
deduplication mechanisms, retries, exceptions, observability, or
implementation technology.
