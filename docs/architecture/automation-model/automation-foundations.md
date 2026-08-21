# Automation Foundations

## Purpose

The Automation Model defines how and when a Workflow Execution may be
initiated automatically. It connects the occurrence defined by the
Execution Model with an automated initiation mechanism; it does not
redefine workflow type, applicability, transformation semantics, execution
identity, outcome, result, or state transformation.

```text
Workflow Model: What may happen?
Execution Model: What does it mean for it to happen?
Automation Model: How and when may it be initiated automatically?
```

These responsibilities are distinct.

```text
Automation != Workflow
Automation != Workflow Execution
```

## Automation

An Automation is a persistent conceptual association between a Trigger,
optional Automation Conditions, and an applicable Workflow, capable of
producing an Execution Request when its conditions are satisfied.

```text
Trigger + Automation Conditions + Workflow
                    ↓
                Automation
```

An Automation does not itself perform work, evaluate applicability, or
produce a result. It initiates or coordinates the possibility of an
Execution Request; the Execution Model governs what happens from that
point forward.

```text
Automation != Execution Request
Automation != Workflow Execution
```

An Automation may exist and never produce an Execution. It may be
inactive, its conditions may never be satisfied, or the associated
Workflow may never become applicable. None of these cases is an
architectural failure.

## Automation Identity

Every Automation has distinguishable conceptual identity, allowing
separate automations to be associated with their own configuration,
triggers, conditions, lifecycle state, and history.

```text
Automation Identity != Workflow Identity
Automation Identity != Execution Identity
Automation Identity != Domain Object Identity
```

When an Automation is independently represented, its identity remains
stable under the Representation Model. This does not promote Automation
to a Domain Object: the Representation Model permits independently
represented architectural concepts when continuity requires it.

## Automation and Workflow

The Workflow Model remains authoritative for workflow type, preconditions,
applicability, transformation semantics, and results. An Automation
references an applicable Workflow; it does not select, define, or make it
applicable.

```text
Automation
    ↓
references
    ↓
Workflow
    ↓
remains authoritative for applicability
```

An Automation may reference at most the Workflow it was configured for. It
does not introduce a second workflow definition, a workflow variant, or a
parallel applicability mechanism.

## Automation and Execution

An Automation may, when its conditions are satisfied and the referenced
Workflow is applicable, produce an Execution Request. The Execution Model
remains authoritative for what happens after that point.

```text
Automation
    ↓
may produce
    ↓
Execution Request
    ↓
governed by the Execution Model
```

```text
Automation != Execution
Automation Triggered != Execution Occurred
```

An Automation is not an Actor. When an Automation produces an Execution
Request, the participating Actor is one of the Actor kinds already
established by the Execution Model.

## Automation Lifecycle

An Automation has a conceptual lifecycle distinguishing whether it is
currently eligible to respond to a Trigger.

```text
Defined
    ↓
Active  ⇄  Suspended
    ↓
Retired
```

```text
Automation Exists != Automation Active
```

An inactive (suspended, not yet activated, or retired) Automation may
still exist as a represented configuration. It does not evaluate
Triggers or produce Execution Requests while inactive.

This lifecycle is conceptual. It does not require a specific stored
status field, state machine implementation, or workflow engine.

## Actor and Automation

An Automation is configured, owned, activated, or suspended by an Actor.
When an Automation responds to a Trigger, the initiating Actor for the
resulting Execution Request is one of the Actor kinds already defined by
the Execution Model: Human, Deterministic System, AI-Assisted System, or
Hybrid System.

```text
Actor != Automation Semantics
AI != Semantic Authority
```

"Automated system" is not a new Actor type. It is a description of how an
existing Actor kind — typically a Deterministic System, and optionally an
AI-Assisted System — participates without direct human initiation at the
moment of the Trigger. AI remains optional and gains no special
architectural authority through Automation.

## Automation Control Boundary

An Automation requires a minimal control boundary to be coherent: whether
it is currently active, what Workflow it is scoped to, and who owns or
configured it.

```text
Automation Control != Authorization
Automation != Capability
```

This model does not define permission policy, actor capability models,
authorization roles, approval chains, or access control. As with
Capability and Authority in the Workflow Model, those concerns belong to
later architectural or implementation layers. An Automation's active/
inactive state and its scope to a single Workflow are the only control
concepts this model requires.

## Boundaries

This model does not define scheduling mechanisms, schedulers, cron,
queues, workers, message brokers, orchestration frameworks, agents,
multi-agent systems, agent memory, LLM providers, prompt engineering,
RAG, APIs, authorization or capability models, retries, errors,
monitoring, UI, storage, or implementation technology.
