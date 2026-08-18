# State and History Experience

## Purpose

Define how Ohtli User Experience presents and distinguishes current state,
derived state, and historical evidence.

The experience must allow an actor to understand the current condition of a
represented object without requiring reconstruction from Events.

This document defines an experience contract. It does not redefine the
semantics established by the canonical Domain, Interaction, Event, Workflow,
or Representation Models.

## Scope

This document defines the experience of:

- Current State;
- Authoritative State;
- Derived State;
- Historical Evidence;
- present versus historical perspectives;
- lifecycle history;
- Archive;
- Reactivate;
- identity continuity across lifecycle changes.

This document does not define:

- domain semantics;
- event semantics;
- representation schemas;
- Markdown schemas;
- YAML schemas;
- filesystem layout;
- database schemas;
- UI components;
- navigation;
- APIs;
- automation;
- agents;
- implementation architecture.

## Relationship with the Representation Model

The User Experience Model consumes the semantics established by the
Representation Model.

The following distinctions are preserved:

Current State
    ≠
Historical Evidence

and:

Authoritative State
    ≠
Derived State

The experience must make these distinctions understandable to the actor
without requiring inspection of the underlying representation.

Current State exists independently of Event reconstruction.

The experience must therefore not require:

Events
  ↓
Replay
  ↓
Current State

as the only way to understand the current condition of an object.

## Current State as the Primary Experience

When an actor enters the experience of a represented object, Current State is
the primary entry point for understanding its present condition.

The experience follows:

Current Object
      ↓
Current State
      ↓
Current Situation
      ↓
Understanding

Historical Evidence remains directly accessible for further investigation.

This establishes an experience priority:

Current State
      ↓
History

It does not establish an authority hierarchy:

Current State > Historical Evidence

Experience priority and architectural authority are distinct concepts.

## Authoritative State and Derived State

The experience must preserve the distinction between authoritative state and
derived information.

Authoritative State represents the state defined as authoritative by the
canonical representation semantics.

Derived State or derived information may provide useful contextual,
analytical, or interpretive information.

The experience must not silently present derived information as authoritative
state.

For example:

CURRENT STATE

Lifecycle:
  Active

Status:
  Validation Failed

DERIVED INFORMATION

The failure may be related to the latest schema change.

The concrete presentation mechanism is intentionally unspecified.

The architectural requirement is that the semantic distinction remains
understandable through the experience.

## Historical Evidence

Historical Evidence is a distinct dimension of the object's experience.

It must remain directly accessible without requiring the actor to first
construct an explanation of the current state.

The experience therefore provides:

Current Object
     │
     ├── Current State
     │
     └── History

The actor may follow either of two legitimate paths:

Understand the present
        ↓
Current State

or:

Investigate what happened
        ↓
Historical Evidence

Historical Evidence must not be presented as Current State.

Therefore:

Current State
      ≠
Historical Evidence

## Present and Historical Perspectives

The experience distinguishes present state from historical evidence as
separate temporal perspectives.

OBJECT
  │
  ├── CURRENT
  │
  └── HISTORY

Current represents the present condition of the object.

History represents evidence concerning what happened or what was represented
in the past.

Historical Evidence may contain temporal information and event-related
evidence, but Current State must not be presented merely as the final point of
a historical timeline.

The experience must not imply:

Events
  ↓
Timeline
  ↓
Current State

as a required architectural mechanism.

## Historical Evidence and Interpretation

Historical Evidence must remain distinguishable from interpretations or
explanations derived from that evidence.

The conceptual relationship is:

Historical Evidence
        ↓
      observed
        ↓
  Interpretation
        ↓
      derived

For example:

HISTORICAL EVIDENCE

Aug 12
  Validation failed

Aug 12
  Schema changed

may support:

DERIVED INFORMATION

The schema change may be related to the validation failure.

The derived interpretation must not become indistinguishable from the
historical evidence.

This distinction also applies to future analytical or AI-assisted
experiences.

An actor may receive an interpretation generated from evidence, but the
interpretation must not alter or retrospectively redefine the evidence.

## Lifecycle History

Lifecycle changes are experienced as changes to the state of the same object.

For example:

Created
   ↓
Active
   ↓
Archived
   ↓
Active

The object maintains identity throughout the lifecycle.

The experience therefore preserves:

Same Identity
      │
      ├── Active
      ├── Archived
      └── Active

Historical Evidence preserves the continuity of those changes.

Lifecycle transitions do not create a new identity merely because the
object's current lifecycle state has changed.

## Archive

Archive must be experienced as a lifecycle state of the same object.

An archived object remains experientially identifiable and inspectable as the
same object.

The experience must communicate:

Object
  ↓
Same Identity
  ↓
Archived

and must not imply:

Archive
  ↓
Object no longer exists

Therefore:

Archive
    ≠
Delete

and:

Archive
    ≠
Identity Destruction

Archive must also not imply informational inaccessibility.

An archived object may remain available for inspection and historical
understanding, subject to the canonical lifecycle semantics.

## Reactivate

Reactivate is experienced as a transition of the same object from an archived
lifecycle state to an active lifecycle state.

Archived
    ↓
Reactivate
    ↓
Active

Reactivate does not create a new object.

The experience preserves:

Same Identity
      │
      ├── Archived
      └── Active

Historical Evidence preserves the lifecycle continuity:

Created
   ↓
Activated
   ↓
Archived
   ↓
Reactivated

Therefore:

Reactivate
    ≠
Create

and:

Reactivate
    ≠
New Identity

## Identity Continuity

Identity continuity must remain understandable across historical lifecycle
changes.

An object may move between lifecycle states without losing its identity.

Conceptually:

                    SAME IDENTITY
                         │
          ┌──────────────┼──────────────┐
          ↓              ↓              ↓
        Active        Archived        Active
          │              │              │
          └──────────────┴──────────────┘
                         ↓
                       History

The experience must therefore preserve the relationship between:

- the object currently being experienced;
- its current lifecycle state;
- its historical lifecycle changes.

## Historical Presence

Historical presence must not imply current presence.

Historical Evidence may demonstrate that an object:

- existed;
- was active;
- was related to another object;
- underwent a lifecycle transition;
- participated in an Event.

None of these facts alone implies that the object is currently active.

Therefore:

Historical Presence
    ≠
Current Presence

Historical presence also does not imply informational inaccessibility:

Historical Presence
    ≠
Informational Inaccessibility

## Event Independence

The experience may expose historical information derived from Events or other
historical evidence.

However, the experience must not introduce Event Sourcing as an architectural
requirement.

In particular, it must remain possible to understand Current State without
replaying Events.

The relationship is:

Current State
      │
      └── independently available

Historical Evidence
      │
      └── available for investigation

Events may contribute to Historical Evidence, but Historical Evidence is not
defined as a mechanism for reconstructing Current State.

## Technology Independence

The experience contract is independent of implementation technology.

The same conceptual experience must be implementable using substantially
different representation technologies.

For example:

Document / Filesystem Representation
              │
              ├──────────────┐
              │              │
              ↓              ↓
         Current State    History

Relational / Database Representation
              │
              ├──────────────┐
              │              │
              ↓              ↓
         Current State    History

The implementation technology may differ, while the experience semantics
remain unchanged.

This document therefore does not define:

- document formats;
- database schemas;
- filesystem structures;
- serialization formats;
- UI frameworks.

## Actor Independence

The experience is independent of a specific actor implementation.

The experience may be consumed by:

- a human actor;
- a deterministic software system;
- an AI-assisted system;
- a hybrid system.

An AI-assisted system may produce derived interpretations from historical
evidence, but such interpretations remain distinguishable from:

Authoritative State

and:

Historical Evidence

The model therefore operates without requiring AI.

## Experience Model

The consolidated experience can be represented conceptually as:

                         CURRENT OBJECT
                               │
                  ┌────────────┴────────────┐
                  ↓                         ↓
             CURRENT STATE              HISTORY
                  │                         │
                  ↓                         ↓
             PRESENT                  HISTORICAL
            CONDITION                  EVIDENCE
                  │                         │
                  │                         ↓
                  │                    INTERPRETATION
                  │                         │
                  ↓                         ↓
             UNDERSTAND                INVESTIGATE
                  │                         │
                  └────────────┬────────────┘
                               ↓
                         UNDERSTANDING

The lifecycle dimension remains:

                    SAME IDENTITY
                         │
          ┌──────────────┼──────────────┐
          ↓              ↓              ↓
        Active        Archived        Active
          │              │              │
          └──────────────┴──────────────┘
                         ↓
                       History

## Invariants

The following experience invariants are established:

Current State
    ≠
Historical Evidence

Authoritative State
    ≠
Derived State

Historical Evidence
    ≠
Interpretation

Current State
    does not require
Event Reconstruction

Archive
    ≠
Delete

Reactivate
    ≠
Create

Archive
    preserves identity

Reactivate
    preserves identity

Historical Presence
    ≠
Current Presence

Historical Presence
    ≠
Informational Inaccessibility

## Architectural Boundaries

This experience model does not introduce new concepts into the canonical
Domain, Interaction, Event, Workflow, or Representation Models.

It defines how concepts already established by those models are experienced.

The dependency direction remains:

Canonical Models
      ↓
Representation
      ↓
User Experience
      ↓
Actor

User Experience must not redefine canonical semantics.

## Relationship with Future UX Work

This document establishes the state and history experience foundation for
subsequent User Experience work.

Future issues may define:

- relationship experience;
- workflow experience;
- navigation and discovery;
- broader experience composition;
- eventual User Experience Model consolidation.

Those future concerns must build on the distinctions established here.

They must not collapse:

Current State
Historical Evidence
Derived Information
Interpretation

into a single undifferentiated experience.

## Status

Status: Canonical

Phase: User Experience

Milestone: 5

Issue: 3 — Define State and History Experience
