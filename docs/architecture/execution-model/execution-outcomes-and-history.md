# Execution Outcomes and History

## Purpose

This contract defines how a Workflow Execution reaches an accountable outcome,
may produce a result, may realize a State Transformation, and remains
historically distinguishable. It preserves the Workflow Model's transformation
semantics and the Event Model's historical semantics.

## Outcome and Result

An Execution Outcome is the conclusion of a particular Workflow Execution in
its Execution Context. An Execution Result is the result produced when the
applicable Workflow defines one.

```text
Workflow Execution → Execution Outcome → Execution Result
```

Outcome makes the occurrence accountable; Result carries the meaning defined
by the applicable Workflow.

```text
Execution != Outcome
Execution != Result
Result != Current State
```

The model introduces no generic success, failure, retry, or error taxonomy.
For operational Execution, the existing result semantics remain authoritative:
Progress, Maintenance, Outcome Reached, No Effective Change, and Degradation.
They do not become required stored statuses.

## Result and State Transformation

A result may be persistent or non-persistent according to the applicable
Workflow and Representation contracts.

```text
Workflow Execution
        ↓
Result
  ├── no State Transformation
  └── State Transformation → Updated State
```

```text
Workflow Execution != State Change
Execution Result != Current State
```

An execution may produce a useful result without changing represented state.
When a result is explicitly representational, it may realize the Workflow
Model's transformation semantics. It must satisfy applicable Representation
Invariants before it becomes Current State.

```text
Result → Representation Contracts and Invariants
          ├── accepted → Updated Current Representation
          └── not accepted → not Current State
```

The Execution Model does not decide which state a workflow may transform.

## Transformation and Reality

An Execution is the occurrence in which a Workflow transformation may be
realized. Operational Execution may involve Reality or Environment and must be
evaluated against actual, not intended, operational results.

```text
Intended Result != Actual Operational Result
```

Recognizing Outcome Reached does not itself enact a lifecycle transition.
Domain identity and lifecycle semantics remain authoritative in their existing
models.

## Execution History

Execution History is the historical association of distinguishable executions
with their Workflow, relevant context, outcome, result, and any transformation.
It preserves that an occurrence happened without treating the past occurrence
as a present condition.

```text
Execution History != Current Applicability
Execution History != Current State
```

History may associate an execution with the represented object already within
the applicable Workflow's scope. It creates no Interaction Model relationship
type and changes no relationship meaning, direction, or cardinality.

Execution identity distinguishes repeated occurrences. When independently
represented, it remains stable even if an associated object is renamed,
relocated, archived, or reactivated.

## Execution and Event

Execution and Event have separate responsibilities.

| Concept | Meaning |
| --- | --- |
| Workflow Execution | An occurrence or attempt to perform a Workflow. |
| Event | Immutable evidence of a completed observable fact affecting Domain Objects. |

```text
Execution != Event
```

A completed execution may yield an observable fact that is preserved as an
Event when the Event Model applies. An Event does not by itself establish a
general execution occurrence. Execution History may refer to Event evidence,
but it is not Event History and does not replace it.

Neither Event nor Execution replay is required to understand Current State.

## Cross-Model Consistency

- **Domain Model:** Execution creates no Domain Object and changes neither
  identity nor lifecycle semantics.
- **Interaction Model:** Execution creates no relationship semantics.
- **Event Model:** Events remain immutable evidence; Execution remains
  distinct.
- **Workflow Model:** It remains authoritative for preconditions,
  applicability, transformations, and results.
- **Representation Model:** Accepted transformations preserve all applicable
  representation invariants; independently represented execution identity is
  stable.
- **User Experience Model:** Historical execution remains distinct from current
  applicability; result remains distinct from Current State.

## Boundaries

This contract does not define audit storage, event sourcing, outcome taxonomies,
retries, exceptions, observability, lifecycle policy, or implementation
technology.
