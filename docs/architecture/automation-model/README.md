# Automation Model

## Status

Defined

## Purpose

The Automation Model defines how and when a Workflow Execution may be
initiated automatically. It connects the Execution Model's distinguishable
occurrences with an automated initiation mechanism without redefining
workflow semantics, execution semantics, or introducing a second Workflow
or Execution Model.

```text
Workflow Model: What may happen?
Execution Model: What does it mean for it to happen?
Automation Model: How and when may it be initiated automatically?
```

These responsibilities are architectural boundaries, not runtime stages.

## Scope

The model consolidates Automation, Automation Identity, Automation
Lifecycle, Trigger, Automation Condition, evaluation outcomes, Actor
participation, and Automation History.

Detailed contracts:

- [Automation Foundations](automation-foundations.md)
- [Automation Triggers and Conditions](automation-triggers-and-conditions.md)

Illustrative, non-normative material:

- [Integration Points](integration-points.md) — relocated from the
  superseded `docs/automation/` scaffolding; carries no architectural
  authority.

## Core Model

```text
Automation
    references an applicable Workflow
        ↓
Trigger
    ↓
Automation Evaluation
    ↓
Automation Conditions
        ├── fail → no Execution Request
        └── pass
              ↓
        Workflow Applicability
              ├── not applicable → no Execution Request
              └── applicable
                    ↓
              Execution Request
                    ↓
              Workflow Execution
                    ↓
              Execution Outcome
                    ↓
              Execution Result
                    ├── no State Transformation
                    └── State Transformation → Updated Current State
```

A Trigger occurring does not guarantee an Execution Request. An Execution
Request does not guarantee a Workflow Execution occurred, nor that it
changed state.

## Canonical Distinctions

```text
Automation != Workflow
Automation != Workflow Execution
Automation != Execution Request
Trigger != Automation Condition
Automation Condition != Workflow Precondition
Trigger != Event
Automation Exists != Automation Active
Automation Triggered != Execution Occurred
Automation != State Change
Automation Control != Authorization
Automation != Capability
```

## Automation and Workflow

The Workflow Model remains authoritative for workflow type, preconditions,
applicability, transformation semantics, and results. An Automation
references an applicable Workflow; it does not select, define, or make it
applicable, and it does not introduce a parallel applicability mechanism.

## Automation and Execution

The Execution Model remains authoritative for Execution Request, Workflow
Execution, Actor participation, Execution Context, Outcome, Result, and
Execution History. An Automation may, when conditions are satisfied and
the referenced Workflow is applicable, produce an Execution Request; it
does not perform, evaluate, or represent the Execution itself.

```text
Automation
    ├── Trigger α → Execution Request → Workflow Execution → Result
    ├── Trigger β → conditions fail → no Execution Request
    └── Trigger γ → conditions pass, not applicable → no Execution Request
```

An Automation may exist without ever producing an Execution. This is not
an architectural failure.

## Triggers and Conditions

A Trigger is a conceptual signal that begins Automation evaluation. An
Automation Condition is a constraint specific to a particular Automation
that must hold, in addition to Workflow preconditions, for evaluation to
proceed.

```text
Trigger != Automation Condition
Automation Condition != Workflow Precondition
```

Automation Conditions are additional and automation-specific; they never
substitute for or override Workflow Applicability, which remains solely
determined by the Workflow Model. This model defines no trigger taxonomy
and no condition expression language.

## Automation Lifecycle and Control

An Automation has a conceptual lifecycle: Defined, Active, Suspended, and
Retired. An inactive Automation may exist as a represented configuration
without evaluating Triggers or producing Execution Requests.

```text
Automation Exists != Automation Active
```

The only control concepts this model requires are an Automation's
active/inactive state and its scope to a single Workflow. It does not
define permission policy, capability models, authorization roles, or
access control.

```text
Automation Control != Authorization
```

As with Capability and Authority in the Workflow Model, fine-grained
authorization belongs to later architectural or implementation layers.

## Actor and Automation

An Automation is configured, owned, activated, or suspended by an Actor.
When an Automation initiates an Execution Request, the participating
Actor is one of the kinds already established by the Execution Model:
Human, Deterministic System, AI-Assisted System, or Hybrid System.
"Automated system" is not a new Actor type — it describes how an existing
Actor kind participates without direct human initiation at the moment of
the Trigger. AI is optional and has no special architectural authority.

## Automation and Events

Automation Triggers and Events have separate responsibilities.

```text
Trigger != Event
```

An Event, when the Event Model applies, may serve as one conceptual
source of a Trigger. Not every Trigger corresponds to an Event, and not
every Event is a Trigger.

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

Any resulting state transformation remains governed by the Workflow Model
and must satisfy applicable Representation Invariants, exactly as for a
non-automated Execution.

## Automation History

Automation History is the historical association of an Automation with
its configuration, activation and suspension, Trigger occurrences,
evaluation outcomes, and any resulting Execution Requests and Workflow
Executions.

```text
Automation History != Event History
Automation History != Execution History
Automation History != Current Applicability
```

Not every internal Automation operation must become an Event. Neither
Event nor Automation replay is required to understand Current State.

## Cross-Model Consistency

| Model | Preserved contract |
| --- | --- |
| Domain Model | Automation creates no Domain Object and does not redefine identity or lifecycle. |
| Interaction Model | Automation creates no relationship meaning, direction, or cardinality. |
| Event Model | Events remain immutable evidence; a Trigger is not an Event. |
| Workflow Model | Workflow semantics, applicability, transformation, and results remain authoritative. |
| Execution Model | Execution Request, Workflow Execution, Actor participation, Outcome, Result, and Execution History remain authoritative. |
| Representation Model | Accepted transformations preserve invariants; independently represented Automation identity is stable. |
| User Experience Model | Automation existing, active, triggered, an Execution occurring, and a state change remain distinguishable. |

## Architectural Boundaries

The Automation Model does not define scheduling mechanisms, schedulers,
cron, queues, workers, message brokers, orchestration frameworks, agents,
multi-agent systems, agent memory, LLM providers, prompt engineering,
RAG, APIs, authorization or capability models, retries, errors,
monitoring, UI, storage, schemas, classes, services, or implementation
technology.

It is complete without a scheduling technology or AI.

## Phase 7 Result

Phase 7 establishes the semantic boundary between an actual occurrence of
a Workflow and the automated mechanism that may initiate it.

```text
Canonical Models
        ↓
Representation Model
        ↓
User Experience Model
        ↓
Execution Model
        ↓
Automation Model
        ↓
Future Implementation
```

This expresses semantic dependency only; it is not runtime order, data
flow, or implementation architecture.
