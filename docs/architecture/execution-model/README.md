# Execution Model

## Status

Defined

## Purpose

The Execution Model defines what it means for an Ohtli Workflow to happen. It
connects the Workflow Model's possible transformations with actual,
distinguishable occurrences without redefining workflow semantics or
introducing Automation.

```text
Workflow Model: What may happen?
Execution Model: What does it mean for it to happen?
Automation: How and when is execution initiated automatically?
```

These responsibilities are architectural boundaries, not runtime stages.

## Scope

The model consolidates Workflow Execution, Execution Request, Actor
participation, Execution Context, Outcome, Result, State Transformation,
execution identity, and Execution History.

Detailed contracts:

- [Execution Foundations](execution-foundations.md)
- [Execution Outcomes and History](execution-outcomes-and-history.md)

## Core Model

```text
Workflow
    defines a possible transformation
        ↓
Execution Request
    may express intent to initiate it
        ↓
Workflow Execution
    is a distinguishable occurrence or attempt
        ↓
Execution Outcome
        ↓
Execution Result
    ├── no State Transformation
    └── State Transformation, when applicable
            ↓
      Updated Current State
```

An Execution Request is not an Execution. An execution may have a result
without changing state. A state transformation updates Current State only when
the canonical Workflow and Representation contracts accept it.

## Canonical Distinctions

```text
Workflow != Workflow Execution
Execution Request != Execution
Applicability != Capability != Authority != Execution
Execution != State Change
Execution != Result
Result != Current State
Execution != Event
Execution != Automation
```

## Workflow and Execution

The Workflow Model remains authoritative for workflow types, preconditions,
applicability, transformation semantics, and workflow results. The Execution
Model does not select or make a workflow applicable; it makes its particular
occurrences distinguishable.

```text
Workflow W
    ├── Execution α
    ├── Execution β
    └── Execution γ
```

Each execution is conceptually distinguishable. It requires independent
representation and stable continuity only when its context, outcome, result,
transformation, or history must be retained as such. Execution does not thereby
become a Domain Object.

## Actor and Context

An execution may involve a Human, Deterministic System, AI-Assisted System, or
Hybrid System. Actors can initiate, perform, or assist an occurrence, but do
not alter workflow, domain, relationship, state, or representation semantics.
AI is optional and has no special architectural authority.

Execution Context is the bounded relevant information that makes an occurrence
intelligible. It may use Workflow-Facing Representation and authorized Relevant
Context; it is not automatically Authoritative State or a new Domain Object.

## Outcome, Result, and State

An Outcome concludes a particular execution. Its Result remains governed by the
applicable Workflow; no general execution-status or failure taxonomy is added.

An execution may yield a non-persistent result. When a result realizes a
representational transformation, it must preserve all applicable Representation
Invariants before it becomes Current State.

For the operational Execution Workflow, its established results remain
unchanged: Progress, Maintenance, Outcome Reached, No Effective Change, and
Degradation. Outcome Reached does not automatically enact a lifecycle
transition.

## Identity, History, and Events

Execution identity distinguishes repeated occurrences and supports association
with their context, outcome, result, transformation, and history. When
independently represented, that identity remains stable.

Execution History is distinct from Current State and current applicability.
It may refer to Event evidence but is not Event History.

```text
Execution != Event
Execution History != Event History
Current State != Historical Evidence
```

A completed execution may produce an observable fact preserved as an Event when
the Event Model applies. Neither Event nor Execution replay is required to
understand Current State.

## Cross-Model Consistency

| Model | Preserved contract |
| --- | --- |
| Domain Model | Execution creates no Domain Object and does not redefine identity or lifecycle. |
| Interaction Model | Execution creates no relationship meaning, direction, or cardinality. |
| Event Model | Events remain immutable evidence of observable completed facts. |
| Workflow Model | Workflow semantics, applicability, transformation, and results remain authoritative. |
| Representation Model | Accepted transformations preserve invariants; Current State requires no replay. |
| User Experience Model | Request, applicability, availability, authority, execution, result, and state change remain distinguishable. |

## Architectural Boundaries

The Execution Model does not define automation policy, scheduling, agents,
orchestration, queues, workers, APIs, AI infrastructure, authorization,
capability models, retries, errors, monitoring, UI, storage, schemas, classes,
services, or implementation technology.

It is complete without Automation or AI.

## Phase 6 Result

Phase 6 establishes the semantic boundary between a workflow's possible
transformation and an actual occurrence of that workflow.

```text
Canonical Models
        ↓
Representation Model
        ↓
User Experience Model
        ↓
Execution Model
        ↓
Future Automation / Implementation
```

This expresses semantic dependency only; it is not runtime order, data flow,
or implementation architecture.
