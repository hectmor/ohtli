# Relationship Experience

## Status

Defined

## Purpose

Define how users understand, inspect, and navigate relationships between
represented objects while preserving the semantics of the canonical
Interaction Model.

The experience must make relationships understandable within an
object-centered workspace without redefining relationship semantics or
introducing implementation-specific concepts.

## Architectural Context

The Interaction Model is authoritative for relationship semantics.

The Representation Model preserves:

- relationship meaning;
- relationship direction;
- relationship cardinality;
- stable identity.

The User Experience Model determines how these semantics become understandable
to users.

The UX must not redefine the canonical relationship model.

Conceptually:

Interaction Model
→ Relationship Semantics
→ Representation
→ User Experience
→ Presentation

The presentation layer must not alter the underlying relationship semantics.

## Relationship Semantics

A relationship is experienced through its canonical semantics.

The experience preserves:

- Meaning
- Direction
- Cardinality
- Identity

Distinct canonical relationships remain distinguishable even when they connect
the same objects.

For example:

    Object A
       ├── owns ───────→ Object B
       └── depends on ─→ Object B

These relationships must not be reduced to a generic:

    Object A ── related to ──→ Object B

The UX communicates relationship semantics but does not create new relationship
types or rules.

## Object-Centered Discovery

Relationships are primarily discovered in the context of the object being
experienced.

Conceptually:

    Object
    │
    ├── State
    ├── Relationships
    ├── History
    └── Workflows

The user begins from an object and discovers the relationships associated with
that object.

This preserves the object-centered experience established by the User
Experience Model.

A global relationship or graph-oriented experience is not required by this
model.

## Relationship Presentation

Relationships are presented through their canonical semantics.

The experience should allow the user to understand what a relationship means,
rather than presenting relationships only as generic connections.

For example:

    Object A
       │
       ├── owns → Object B
       ├── depends on → Object C
       └── belongs to → Object D

The concrete visual presentation remains implementation-independent.

The UX defines what must be understandable, not which UI component, layout,
framework, or visual notation must be used.

## Relationship Direction

Relationship direction must remain explicit whenever direction is part of the
canonical relationship semantics.

For example:

    Object A ── owns ──→ Object B

When experienced from Object B, the same relationship may be expressed as:

    Object B
      ←── owned by ── Object A

The change in perspective must not change the underlying relationship.

The experience must preserve the distinction between:

    A owns B

and:

    B owns A

when those represent different semantics.

## Relationship Cardinality

Cardinality is defined by the canonical Interaction Model.

The UX communicates cardinality when it is relevant to understanding the
relationship.

The experience does not require a particular formal notation.

For example, the following may communicate the relevant semantics:

    Project

    Tasks
      12 related tasks

without requiring a specific notation such as:

    1 ── contains ── 0..*

The specific presentation of cardinality remains implementation-independent.

The UX must communicate cardinality without redefining its rules.

## Stable Identity

Related objects remain identifiable through their stable identity.

Moving from one object to a related object must not cause the target object's
identity to depend on:

- its position in the interface;
- its current relationship;
- a contextual label;
- a presentation-specific identifier.

Conceptually:

    Object A
       │
       │ owns
       ↓
    Object B

Object B remains the same represented object regardless of how it is reached.

## Relationship Context During Navigation

Moving to a related object changes the current object context while preserving
sufficient relationship context to explain the transition.

Conceptually:

    Origin
      ↓
    Relationship
      ↓
    Target

For example:

    Object A
       │
       │ owns
       ↓
    Object B

When Object B becomes the current object, the experience must preserve enough
context for the user to understand:

    Object A → owns → Object B

The concrete navigation mechanism is outside the scope of this document.

This requirement does not define:

- URLs;
- routes;
- breadcrumbs;
- navigation components;
- frontend frameworks;
- implementation-specific navigation systems.

It defines an experiential property:

    Navigation
        ↓
    preserves relationship context

## Current and Historical Relationships

Current and historical relationships are distinct temporal dimensions of the
relationship experience.

Conceptually:

    Object
    │
    ├── Current State
    ├── Current Relationships
    ├── History
    │   └── Historical Relationships
    └── Workflows

The distinction follows the principle established by the State and History
Experience:

    Current State
        ≠
    Historical Evidence

Applied to relationships:

    Current Relationship
        ≠
    Historical Relationship

A historical relationship remains accessible as historical evidence without
being interpreted as a current relationship.

The temporal status of a relationship must remain distinct from the identity
and meaning of the relationship.

## Lifecycle and Relationships

Object lifecycle state and relationship semantics are independent dimensions.

An object's lifecycle state does not, by itself, change the semantic identity
of its relationships.

For example:

    Object A
       │
       └── owns → Object B
                     │
                     └── Archived

The fact that Object B is archived does not automatically imply:

    Object A
       └── historically owned → Object B

Whether a relationship is current or historical is determined by the canonical
model, not inferred solely from the lifecycle state of either object.

Conceptually:

    Object Lifecycle State
        ≠
    Relationship Temporal Status

## Archive

Archive does not cause an object to lose its identity.

A relationship involving an archived object remains semantically
understandable.

The experience may communicate that the related object is archived, while
preserving the relationship itself.

Archive therefore does not automatically transform:

    Current Relationship

into:

    Historical Relationship

The canonical model determines the temporal status of the relationship.

## Reactivation

Reactivation preserves the identity of the represented object.

Conceptually:

    Same Object
         │
         ├── Archived
         │
         └── Reactivated
                │
                └── Same Identity

Reactivation does not create a new object merely because the object was
previously archived.

Likewise, reactivation does not automatically create new relationships.

Relationship continuity or change is determined by the canonical model.

Therefore:

    Object Lifecycle
        ≠
    Relationship Lifecycle

and:

    Reactivate
        ≠
    Create

## Multiple Relationships Between the Same Objects

Distinct canonical relationships between the same objects remain distinguishable
in the experience.

For example:

    Object A
       ├── owns ───────→ Object B
       └── depends on ─→ Object B

The experience must preserve the distinction between these relationships.

The objects being identical does not make the relationships identical.

Each relationship retains its:

- meaning;
- direction;
- cardinality;
- identity;
- temporal status when applicable.

## Relationship Experience Within the Object Workspace

Relationships are experienced as part of the object's contextual workspace.

Conceptually:

    Object
    │
    ├── State
    ├── Relationships
    │   ├── Related Object A
    │   ├── Related Object B
    │   └── ...
    ├── History
    └── Workflows

Moving to a related object establishes that object as the new current object
while preserving enough relationship context to explain the transition.

This preserves both:

- object-centered experience;
- relationship continuity.

## Architectural Boundaries

This document defines experience-level semantics.

It does not introduce:

- new relationship types;
- new cardinality rules;
- new Domain Objects;
- graph database concepts;
- database schemas;
- UI frameworks;
- implementation-specific navigation systems.

The canonical Interaction Model remains authoritative.

The UX may communicate canonical semantics, but it must not redefine them.

## Design Principles

The relationship experience follows these principles:

1. Relationships are discovered from the current object context.
2. Relationships are experienced through their canonical meaning.
3. Direction is preserved explicitly when semantically relevant.
4. Cardinality is communicated when relevant to understanding.
5. Stable identity is preserved across related objects.
6. Navigation preserves sufficient relationship context.
7. Current and historical relationships remain distinguishable.
8. Object lifecycle state does not automatically redefine relationship semantics.
9. Archive preserves object identity.
10. Reactivation preserves object identity and canonical relationship semantics.
11. Distinct canonical relationships remain distinguishable even between the
    same objects.
12. Presentation must not redefine canonical relationship semantics.

## Summary

The relationship experience provides a semantic bridge between the canonical
Interaction Model and the user's understanding of related objects.

The user can:

    Discover
        ↓
    Understand
        ↓
    Inspect
        ↓
    Move

while the underlying relationship semantics remain authoritative and stable.

The experience therefore preserves:

    Meaning
    Direction
    Cardinality
    Identity
    Temporal Status

without coupling those semantics to a particular visual representation or
implementation.
