# Workflow Experience

## Status

Defined

## Purpose

Define how users experience workflow applicability, interaction, execution, and
results without redefining the semantics established by the Workflow Model.

The User Experience Model makes workflow behavior understandable and
interactable while preserving the authority of the canonical Workflow Model and
the Representation Model.

## Architectural Position

The Workflow Model remains authoritative for:

- workflow semantics;
- preconditions;
- applicability;
- transformations;
- resulting system state.

The Representation Model remains authoritative for:

- how workflow-relevant information is represented;
- representation invariants;
- continuity between represented state and the underlying model.

The User Experience Model defines how these concepts are experienced by actors.

The UX must not redefine workflow semantics.

Conceptually:

```text
Workflow Model
      |
      | authoritative semantics
      v
Representation Model
      |
      | represented workflow context
      v
User Experience Model
      |
      | interaction
      v
Actor
```

## Core Principle

The User Experience Model must make workflow applicability, interaction,
execution, and results understandable without collapsing them into one concept
or redefining their canonical semantics.

The experience must preserve the following distinctions:

```text
Applicable
    !=
Available
    !=
Authority
    !=
Execution
    !=
Result
    !=
Current State
```

## 1. Workflow Discovery

Workflows are experienced within the context of the represented object.

Conceptually:

```text
Object
  |
  +-- State
  +-- Relationships
  +-- History
  +-- Workflows
```

Workflow discovery should begin from the relevant object context rather than
requiring users to reconstruct the object's state or history before discovering
what workflows may be relevant.

A workflow may be discovered because it is:

- applicable;
- potentially relevant;
- recommended;
- historically relevant.

Discovery does not imply applicability or execution.

```text
Discovery
    !=
Applicability
    !=
Execution
```

## 2. Applicability

Applicability is a semantic property established by the Workflow Model.

The UX exposes applicability but does not define it.

The experience should make the current applicability of a workflow directly
understandable.

When relevant, the experience may expose the conditions or contextual factors
that explain applicability.

The distinction is:

```text
Workflow Model
    |
    +-- defines applicability
    |
    v
UX
    |
    +-- makes applicability understandable
```

The UX must not create new applicability rules.

### Current Applicability

Current applicability is evaluated against the current object context.

```text
Current State
      |
      v
Current Applicability
```

Historical applicability must not silently become current applicability.

Therefore:

```text
Current Applicability
        !=
Historical Applicability
```

A workflow that was applicable in a previous state may be non-applicable in the
current state.

## 3. Applicability and Availability

Applicability and availability are distinct experiential dimensions.

```text
Applicable
    !=
Available
```

A workflow may be applicable without being available for interaction in the
current experience.

The UX must not imply:

```text
Applicable
    =
Executable
```

Applicability describes whether the workflow is relevant under the current
workflow semantics.

Availability describes whether the workflow can currently be presented for
interaction.

The UX must not redefine authority or authorization through availability.

## 4. Applicability Explanation

When useful, the experience may expose relevant conditions that explain why a
workflow is applicable or non-applicable.

For example:

```text
Approve invoice

Applicable

Reason:
The invoice is pending approval.
```

The explanation is contextual representation of canonical workflow semantics.

It must not become a new source of semantic authority.

Therefore:

```text
Applicability Conditions
        !=
UX Explanation
```

The Workflow Model remains authoritative.

## 5. Execution

Execution is distinct from applicability and availability.

The conceptual interaction is:

```text
Applicable
    |
    v
Available
    |
    v
Execution Requested
    |
    v
Execution
    |
    v
Outcome
```

The experience must not represent a workflow as executed merely because it is:

- discovered;
- applicable;
- available;
- recommended;
- inspected.

Execution represents an actual workflow interaction.

### Execution Identity

Each workflow execution remains distinguishable in the experience.

This does not introduce a new domain object or redefine the Workflow Model.

It only ensures that separate executions can be experienced as separate
interactions.

Conceptually:

```text
Workflow
   |
   +-- Execution 1
   |
   +-- Execution 2
   |
   +-- Execution N
```

The workflow remains the stable semantic concept.

## 6. Confirmation

Confirmation, when applicable to an interaction, is experienced as a distinct
step before execution.

```text
Execution Requested
        |
        v
Confirmation
        |
        v
Execution
```

Confirmation is optional.

It must not be interpreted as execution.

If the actor cancels:

```text
Execution Requested
        |
        v
Confirmation
        |
        v
Cancelled
```

No execution is implied by the cancellation.

The UX does not define:

- authorization;
- security policies;
- permission systems;
- which workflows require confirmation.

It only distinguishes confirmation from execution when confirmation is part of
the experience.

## 7. Results

A workflow execution produces an outcome that must remain distinguishable from
the current state.

Conceptually:

```text
Execution
    |
    v
Result
```

Therefore:

```text
Result
    !=
Current State
```

A result may provide information without changing represented state.

For example:

```text
Analyze invoice
    |
    v
Result: Low risk
```

may produce no state transformation.

The result remains meaningful even when no state change occurs.

## 8. Non-Persistent Results

A workflow may produce a result that does not become persistent represented
state.

Such a result remains associated with its execution context.

Conceptually:

```text
Workflow Execution
       |
       v
Non-Persistent Result
```

The UX must not silently promote such information into authoritative state.

Therefore:

```text
Non-Persistent Result
        !=
Current State
```

The experience may make the result accessible from the relevant execution or
object context without implying that the represented object's authoritative
state has changed.

## 9. State Transformation

When a workflow transforms represented state, the UX communicates the resulting
state without redefining the transformation.

Conceptually:

```text
Workflow Execution
       |
       v
Transformation
       |
       v
Updated State
       |
       v
Current State
```

The resulting representation must continue to satisfy Representation
Invariants.

The UX may communicate:

- that a transformation occurred;
- its resulting outcome;
- the resulting current state.

It must not define the transformation semantics.

## 10. Current State After Execution

When a workflow changes represented state, the updated state becomes the
current state experienced by the user.

The user should not have to reconstruct the new state from the execution
history.

```text
Execution
    |
    v
Updated State
    |
    v
Current State
```

The experience therefore preserves:

```text
Current State
    !=
Reconstructed Event History
```

Historical information may explain how the current state came to exist, but
current state remains directly understandable.

## 11. Unsuccessful Execution

An unsuccessful execution must remain distinguishable from:

- non-applicability;
- unavailability;
- cancellation before execution;
- successful execution.

Conceptually:

```text
Execution
    |
    v
Outcome
    |
    +-- Successful
    |
    +-- Unsuccessful
```

An unsuccessful outcome does not imply that the intended transformation
occurred.

The UX must not represent an unsuccessful execution as successful current
state transformation.

## 12. Execution and History

Workflow executions may contribute to the historical experience, but execution
history must remain distinguishable from state-change history.

```text
History
   |
   +-- Workflow Execution
   |       |
   |       +-- Result
   |
   +-- State Change
           |
           +-- Updated State
```

Therefore:

```text
Workflow Execution
        !=
State Change
```

An execution may produce a result without changing state:

```text
Execution
    |
    v
Result
    |
    v
No State Change
```

Or it may produce a transformation:

```text
Execution
    |
    v
Transformation
    |
    v
State Change
```

The existence of an execution in historical experience must not imply that a
state change occurred.

## 13. Historical Applicability

Historical applicability remains historical evidence.

For example:

```text
Previous State:
Pending

Approve invoice:
Applicable
```

After execution:

```text
Current State:
Approved

Approve invoice:
Not applicable
```

History may still show:

```text
Approve invoice
Executed successfully
```

This is not contradictory because the statements refer to different contexts.

The experience therefore preserves:

```text
Current Applicability
        !=
Historical Applicability
        !=
Historical Execution
```

## 14. Object Context

Workflow interaction remains grounded in the originating object's context.

Moving through workflow interaction should preserve enough context for the actor
to understand:

- which object is involved;
- which workflow is being considered;
- why it is relevant;
- what execution is being requested;
- what result occurred;
- whether state changed.

Conceptually:

```text
Object
   |
   v
Workflow
   |
   v
Execution
   |
   v
Result
```

The workflow experience must not unnecessarily detach the interaction from the
object that gives it meaning.

## 15. Actors

The workflow experience remains semantically consistent across:

- human interaction;
- deterministic system interaction;
- AI-assisted interaction;
- hybrid interaction.

Actor context may be represented, but it does not redefine workflow semantics.

Therefore:

```text
Actor
  !=
Workflow Semantics
```

and:

```text
Human
System
AI
Hybrid
```

may all interact with the same workflow semantics.

AI remains optional.

The UX must not imply:

```text
AI
  =
Required Workflow Mechanism
```

An AI-assisted interaction may assist with:

- discovery;
- explanation;
- recommendation;
- interaction.

It does not acquire authority over:

- applicability;
- execution semantics;
- transformation semantics;
- authoritative state.

## 16. Recommendations

Recommendations may assist workflow discovery and contextual understanding.

A recommendation remains distinct from workflow semantics.

```text
Recommendation
      !=
Applicability
      !=
Availability
      !=
Execution
```

A recommendation may refer to a currently non-applicable workflow.

For example:

```text
Recommended next step:
Close invoice

Currently not applicable.

Reason:
The invoice must be approved first.
```

The recommendation does not imply that the workflow is executable.

This allows the experience to communicate possible future actions without
changing current applicability.

Recommendations remain a UX concern.

This issue does not define:

- recommendation engines;
- ranking algorithms;
- scoring systems;
- AI recommendation architectures.

## 17. Recommendation Reasons

When a workflow is recommended, the experience may expose a contextual reason
for the recommendation.

```text
Recommendation
      |
      +-- Recommendation Reason
```

The reason must remain distinct from canonical workflow applicability
conditions.

```text
Recommendation Reason
        !=
Applicability Conditions
```

For example:

```text
Recommended:

Approve invoice

Why this is recommended:
The invoice has been pending for 5 days.

Applicability:
Applicable
```

The recommendation reason is contextual guidance.

It does not redefine the workflow's semantic preconditions.

## 18. Non-Applicable Workflows

A non-applicable workflow may remain discoverable when it is contextually
relevant.

For example:

```text
Close invoice

Currently not applicable.

Reason:
Approval is still pending.
```

The experience may explain why the workflow is not currently applicable.

However, non-applicability must remain clear.

The UX must not imply:

```text
Discovered
    =
Applicable
```

or:

```text
Recommended
    =
Applicable
```

## 19. Representation Invariants

If workflow execution changes represented state, the resulting representation
must continue to satisfy the Representation Model's invariants.

The workflow experience may communicate the transition:

```text
Before
   |
   v
Execution
   |
   v
After
```

but it does not redefine:

- object identity;
- relationship semantics;
- state semantics;
- representation invariants.

The canonical models remain authoritative.

## 20. Conceptual Workflow Experience

The complete experience can be summarized as:

```text
                         Object Context
                              |
                              v
                     Workflow Discovery
                              |
                 +------------+------------+
                 |                         |
                 v                         v
          Recommendation              Workflow
                 |                         |
                 |                  +------+------+
                 |                  |             |
                 |                  v             v
                 |             Applicability   Availability
                 |                  |             |
                 |                  +------+------+
                 |                         |
                 +-------------------------+
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
                                           v
                                        Outcome
                                       /       \
                                      /         \
                                     v           v
                                  Result   Transformation
                                                |
                                                v
                                          Updated State
                                                |
                                                v
                                          Current State
```

Historical experience remains a parallel contextual dimension:

```text
Workflow Execution
        |
        +------> Historical Experience

State Change
        |
        +------> Historical Experience
```

but:

```text
Execution
    !=
State Change
```

and:

```text
Historical Evidence
    !=
Current State
```

## 21. Architectural Boundaries

This issue defines experience, not execution infrastructure.

It must not define:

- workflow engines;
- schedulers;
- agents;
- LLM providers;
- authorization systems;
- automation policies;
- orchestration frameworks;
- APIs;
- execution architecture;
- database schemas;
- workflow persistence mechanisms.

It also must not introduce:

- new workflow types;
- new workflow semantics;
- new applicability rules;
- new transformation semantics;
- new domain objects.

The canonical Workflow Model remains authoritative.

## 22. Summary

The workflow experience preserves the following distinctions:

```text
Discovery
    !=
Applicability
    !=
Availability
    !=
Recommendation
    !=
Execution
    !=
Result
    !=
Current State
```

And:

```text
Current Applicability
    !=
Historical Applicability
```

```text
Workflow Execution
    !=
State Change
```

```text
Historical Evidence
    !=
Current State
```

The resulting experience allows an actor to understand what workflows are
relevant, why they are relevant, whether they are currently available, what
happened when one was executed, and what state resulted, without requiring the
actor to reconstruct current state from historical execution data.

The experience remains compatible with human, deterministic, AI-assisted, and
hybrid interaction while preserving the canonical semantics of the Workflow
Model.
