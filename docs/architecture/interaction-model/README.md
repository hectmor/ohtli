# Interaction Model

## Purpose

The Interaction Model defines the relationships between the domain
objects of Ohtli.

It answers a single question:

> How are domain objects related?

The Interaction Model does not define workflows, events, user actions,
or implementation details.

---

# Design Principles

## Explicit Relationships

Every relationship has a semantic meaning.

Generic relationships such as "relates to" are not allowed.

---

## Technology Independent

Relationships exist regardless of how they are implemented.

---

## Directional

Relationships are defined from one object toward another.

---

# Relationship Types

## belongs to

Indicates ownership or contextual membership.

## contains

Indicates logical grouping.

## references

Indicates an explicit reference.

## supports

Indicates that one object provides knowledge or context for another.

---

# Domain Objects

- Project
- Area
- Meeting
- Reference
- Resource
- Journal Entry
