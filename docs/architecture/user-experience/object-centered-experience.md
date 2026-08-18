# Object-Centered Experience

## Purpose

Define how a Domain Object serves as the primary contextual center of Ohtli
user experience.

The experience organizes relevant represented state, relationships, history,
context, and interactions around the current object without redefining their
canonical semantics.

## Object as Experience Center

A Domain Object is the primary contextual center of experience.

This does not make the object a container for every element experienced by the
actor.

Instead:

                    Current Object
                         │
          ┌──────────────┼──────────────┐
          ↓              ↓              ↓
        State       Relationships     History
                         │
                         ↓
                  Relevant Context
                         │
                         ↓
                    Interactions

State, relationships, history, and workflows retain the authority and
semantics defined by their respective canonical models.

## Current Situation

Object-centered experience prioritizes the current situation of the object.

The current situation is an experiential view of currently relevant
represented state and context.

It is not a new Domain State.

Therefore:

Current Situation ≠ Domain State

The experience may present:

Object
  ↓
Current Situation
  ↓
Relevant Context
  ↓
Understanding

## Progressive Experience

Represented state remains complete and authoritative.

User experience provides progressive access to that representation according
to the actor's need for understanding.

Representation
      ↓
   complete
      ↓
User Experience
      ↓
progressive access
      ↓
     Actor

Object-centered experience should reveal represented information progressively
while preserving access to the complete representation.

Progressive experience is a UX property and must not alter representation
semantics.

## Inspection

Inspection allows the actor to progressively inspect relevant information
associated with the current object.

Relevant information may include:

- state;
- relationships;
- history;
- relevant contextual information;
- workflow applicability;
- other represented information.

Inspection does not transform representation.

Inspect ≠ Transform

## Related Objects

The actor may move from the current object to a related object through a
canonical relationship.

The related object then becomes the new current object.

Object A
   ↓
Relationship
   ↓
Object B
   ↓
Current Object

The relationship continues to preserve the semantics, direction, and
cardinality defined by the Interaction Model.

UX does not create composite objects from related objects.

## Exploration Context

Object-centered experience may preserve the active path through related
objects that led to the current object.

For example:

Project
   ↓
Production Dataset
   ↓
ETL Pipeline

The current object is:

ETL Pipeline

while the exploration context is:

Project → Production Dataset → ETL Pipeline

There is always one current object.

Exploration context provides experiential context and does not create a new
Domain Object.

## Exploration Context and Domain History

Exploration context is distinct from Domain History.

Domain History
→ historical evidence associated with the represented object

Exploration Context
→ active path followed by the actor during the current experience

Therefore:

Domain History ≠ Exploration Context

Exploration context must not be interpreted as historical evidence.

## Scope of Exploration Context

Exploration context is scoped to the active experience.

It does not become persistent Domain State or Domain History.

Exploration Context ≠ Persistent State
Exploration Context ≠ Domain History

When the active experience ends, the exploration context is no longer
architecturally relevant.

Persistence of navigation, sessions, bookmarks, or workspaces is outside the
scope of this model.

## Relevant Interactions

Object-centered experience prioritizes interactions relevant to the current
situation.

The relationship is:

Current Representation
        ↓
Workflow Applicability
        ↓
Relevant Interactions
        ↓
Actor Decision

UX does not determine workflow applicability.

The Workflow Model remains authoritative for workflow semantics.

The experience may expose applicable interactions without executing them.

Therefore:

Applicability ≠ Presentation
Presentation ≠ Execution
Applicability ≠ Execution

## Interaction and Transformation Boundary

The actor may select a relevant interaction.

The resulting transformation remains governed by the canonical model that
defines its semantics.

For workflows:

Workflow Model
      ↓
Applicability
      ↓
User Experience
      ↓
Relevant Interaction
      ↓
Actor Decision
      ↓
Execution
      ↓
Updated Representation

UX may initiate or request interaction but does not define transformation
semantics.

## Representation Authority

The Representation Model remains authoritative for represented state.

The User Experience Model does not create an alternative representation.

The distinction is:

Representation
    = authoritative and complete

User Experience
    = contextual and progressive

UX organizes access to representation without redefining its semantics.

## Technology Independence

Object-centered experience is independent of implementation technology.

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

The same experience concepts must remain implementable over different
Representation technologies.

## Actor Independence

The model remains usable by:

- humans;
- deterministic systems;
- AI-assisted systems;
- hybrid systems.

AI remains optional.

Different actors may experience the same represented semantics through
different implementations without changing the underlying model.

## Architectural Boundaries

This model does not redefine:

- Domain Objects;
- identity;
- Domain State;
- relationships;
- Events;
- Domain History;
- lifecycle semantics;
- workflow semantics;
- representation invariants.

It defines only how those existing concepts may be experienced around a
current Domain Object.

## Core Principles

1. A Domain Object is the primary contextual center of experience.
2. Experience prioritizes the object's current situation.
3. Current Situation is not a new Domain State.
4. Represented information remains complete and authoritative.
5. Experience may reveal information progressively.
6. Inspection does not transform representation.
7. Related objects may become the new current object.
8. One current object exists at each point of experience.
9. Exploration context may preserve the active path through related objects.
10. Exploration Context is distinct from Domain History.
11. Exploration Context is scoped to the active experience.
12. Relevant interactions are prioritized according to workflow applicability.
13. UX does not determine workflow applicability.
14. Presentation of an interaction does not imply execution.
15. UX does not redefine representation or transformation semantics.
16. The model remains actor-independent and technology-independent.

## Status

Approved as the canonical Object-Centered Experience model for Milestone 5.
