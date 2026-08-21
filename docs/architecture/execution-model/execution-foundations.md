# Execution Foundations

## Purpose

The Execution Model defines what it means for an applicable Ohtli Workflow to
occur. It connects the possibility defined by the Workflow Model with a
particular occurrence; it does not redefine workflow type, preconditions,
applicability, transformation semantics, or workflow meaning.

```text
Workflow Model: What may happen?
Execution Model: What does it mean for it to happen?
Automation: How and when is execution initiated automatically?
```

These responsibilities are distinct.

```text
Workflow != Workflow Execution
Workflow Execution != Automation
```

## Workflow Execution

A Workflow Execution is a distinguishable occurrence or attempt to perform a
particular applicable Workflow in a particular Execution Context. It is
associated with the Workflow whose semantics govern it; it is not a new
workflow, workflow type, or Domain Object.

```text
Applicable Workflow + Execution Context + Actor participation
                            ↓
                    Workflow Execution
```

Separate executions of the same Workflow remain separate occurrences.

## Execution Request

An Execution Request expresses an intention to initiate a Workflow Execution.
It is not an execution.

```text
Execution Request != Workflow Execution
```

A request may be confirmed, declined, withdrawn, or not proceeded with. None
of those cases implies that the Workflow occurred. The model does not require a
separate request for every execution, nor does it require requests to have
independent identity.

## Applicability, Capability, Authority, and Execution

| Concept | Question | Authority |
| --- | --- | --- |
| Applicability | Are workflow preconditions satisfied? | Workflow Model |
| Capability | Can an actor or mechanism perform the work? | Outside this model |
| Authority | Is performance permitted? | Outside this model |
| Execution | Did a particular occurrence happen? | Execution Model |

```text
Applicability != Capability != Authority != Execution
```

Visibility, recommendation, inspection, availability, capability, or authority
does not imply execution. This model neither defines authorization policy nor
actor capabilities.

## Actor Participation

An Actor is a participant that initiates, performs, assists, or otherwise
materially participates in an Execution. Actors may be Human, Deterministic
System, AI-Assisted System, or Hybrid System. Initiation and performance may
have different actors.

```text
Actor != Workflow Semantics
Actor != Domain Semantics
AI != Semantic Authority
```

Actor participation never changes workflow preconditions, transformation,
results, object identity, relationship semantics, or representation invariants.
AI is optional.

## Execution Context

Execution Context is the bounded relevant information in which a particular
execution occurs. As needed by the applicable Workflow, it may include the
Workflow, its established target or scope, Workflow-Facing Representation,
authorized Relevant Context, temporary inputs, environmental conditions,
participating actors, and a request when one exists.

```text
Execution Context != Authoritative State
Execution Context != New Domain Object
Execution Context != Workflow Semantics
```

The model prescribes no universal context structure or persistence mechanism.

## Execution Identity

Every Workflow Execution has distinguishable conceptual identity, allowing
separate occurrences to be associated with their own context, outcome, result,
transformation, and history.

```text
Execution Identity != Workflow Identity
Execution Identity != Domain Object Identity
Execution Identity != Event Identity
Execution Identity != Result Identity
```

When an execution is independently represented, its identity must remain stable
under the Representation Model. This does not promote Execution to a Domain
Object: the Representation Model permits independently represented
architectural concepts when continuity requires it.

## Boundaries

This model does not define workflow types or applicability rules; authorization
or capability models; UI flows; schedulers, agents, queues, workers, APIs;
retries, errors, monitoring; or storage and implementation technology.
