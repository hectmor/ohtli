# UX Foundations

## Purpose

The User Experience Model defines how actors experience and interact with
represented Ohtli state without redefining its semantics.

It establishes the foundation for how Ohtli is experienced while preserving the
authority of the canonical Domain, Interaction, Event, Workflow, and
Representation Models.

## Architectural Boundary

The architectural relationship is:

Canonical Models
      ↓
Representation Model
      ↓
User Experience Model
      ↓
Implementation

The User Experience Model interacts with Representation but does not redefine
its semantics.

UX does not redefine:

- identity;
- state;
- relationships;
- Events;
- lifecycle semantics;
- workflow semantics;
- representation invariants.

## Actor Independence

The User Experience Model is actor-independent.

It can be used by:

- humans;
- deterministic systems;
- AI-assisted systems;
- hybrid systems.

Actor independence does not require identical interfaces.

An implementation may adapt the experience to the capabilities of a specific
actor.

AI remains optional.

## Primary Experience Unit

The represented Domain Object is the primary unit of Ohtli experience.

An actor should be able to experience an object together with its relevant:

- state;
- relationships;
- history;
- workflows;
- contextual information.

This does not imply that every element experienced by an actor is a Domain
Object.

## Capture and Context

Inbox and Journal are UX capture and contextual entry points.

They do not introduce new Domain Objects or Representation Model concepts.

Inbox / Journal
      ↓
Capture
      ↓
Contextual Information
      ↓
Object-centered Experience

Therefore:

Inbox Entry ≠ Domain Object

Journal Entry ≠ automatically Event

Captured information may later be associated with represented objects or
contribute relevant context to their experience.

## Relevant Context

Context may be dynamically incorporated into the experience when it is
relevant to understanding the current situation.

Representation ─────┐
                    ↓
                Understanding
                    ↑
                    │
             Relevant Context

Relevant context may influence an actor's understanding and decisions.

However:

Context ≠ Authoritative State

Relevant Context ≠ New Domain Object

Context must not silently redefine authoritative representation.

The architectural principle is:

> Context can influence an actor's understanding and decisions, but only
> represented state can provide authoritative system semantics.

## Experience Cycle

The conceptual experience cycle is:

Discover
   ↓
Understand
   ↓
Inspect
   ↓
Decide
   ↓
Interact
   ↓
Observe Result
   ↓
Re-evaluate
   ↺

This is a conceptual model of experience, not a mandatory sequence of screens
or UI steps.

An actor may enter or leave the cycle according to the situation.

## Inspection

Inspection observes represented state without transforming it.

Examples include:

- opening an object;
- inspecting state;
- inspecting relationships;
- inspecting history;
- inspecting relevant context;
- inspecting workflow applicability.

Therefore:

Inspect ≠ Transform

Inspection does not change authoritative representation.

## Transformative Interaction

A transformative interaction may initiate or request a transformation through
the appropriate canonical model.

UX does not define or perform the transformation.

The boundary is:

Actor
  ↓
User Experience
  ↓
Interaction / Intent
  ↓
Domain / Workflow Semantics
  ↓
Transformation
  ↓
Updated Representation
  ↓
User Experience

The Workflow Model remains authoritative for workflow transformation
semantics.

The architectural principle is:

> The User Experience Model may initiate or request interactions, but it does
> not define or perform representation transformations.

## Applicability and Execution

UX preserves the distinction:

Applicability ≠ Execution

and:

Applicability ≠ Capability ≠ Authority

UX may expose or allow inspection of workflow applicability, but it does not
define applicability, capability, authority, or execution semantics.

## Observation of Results

After a transformation, the actor can observe the resulting represented
state.

The experience may then re-evaluate the situation because the updated
representation may change:

- current state;
- relevant context;
- relationships;
- history;
- workflow applicability.

Transformation
      ↓
Updated Representation
      ↓
Observe Result
      ↓
Re-evaluate

## Representation Authority

Only canonical representation provides authoritative system semantics.

UX may:

- present representation;
- provide access to representation;
- provide relevant context;
- initiate interactions;
- expose results.

UX must not become an alternative source of system semantics.

## Technology Independence

The User Experience Model is independent of implementation technology.

It must not depend on:

- Markdown;
- YAML;
- filesystem layout;
- databases;
- PostgreSQL;
- Obsidian;
- web frameworks;
- UI frameworks;
- APIs;
- automation frameworks;
- LLM providers.

The same UX concepts must be implementable over different Representation
technologies.

## Relationship with Canonical Models

The User Experience Model consumes and interacts with the results of the
canonical models.

It does not replace them.

Domain Model
      ↓
Interaction Model
      ↓
Event Model
      ↓
Workflow Model
      ↓
Representation Model
      ↓
User Experience Model

The UX Model must preserve the semantics established by those models.

## Architectural Principles

The following principles are established:

1. UX interacts with Representation without redefining its semantics.
2. UX is actor-independent.
3. AI participation is optional.
4. Domain Objects are the primary units of experience.
5. Inbox and Journal provide capture and contextual entry points.
6. Relevant context may influence understanding and decisions.
7. Context does not silently become authoritative representation.
8. Inspection does not transform representation.
9. UX may initiate or request interactions but does not define transformations.
10. Workflow semantics remain authoritative in the Workflow Model.
11. Updated representation becomes the basis for subsequent observation and
    re-evaluation.
12. UX remains independent of implementation technology.

## Future UX Models

This foundation provides the boundary for subsequent User Experience work,
including:

- object-centered experience;
- navigation and discovery;
- state and history experience;
- relationship experience;
- workflow experience;
- capture and contextual experience.

Future UX models must remain consistent with the principles established
here.

## Status

Approved as the canonical UX Foundations for Milestone 5.
