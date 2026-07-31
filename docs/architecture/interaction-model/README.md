# Interaction Model

## Purpose

The Interaction Model defines the semantic relationships between the
domain objects of Ohtli.

It answers a single question:

> How are domain objects related?

The Interaction Model does not define workflows, events, business rules,
cardinality, or implementation details.

---

# Design Principles

## Semantic Relationships

Relationships describe permanent semantic connections between domain
objects.

Every relationship has an explicit meaning.

Generic relationships such as "relates to" are not allowed.

---

## Technology Independent

Relationships exist independently of any implementation technology.

Whether objects are stored as Markdown files, database records, or any
other representation does not change the conceptual model.

---

## Object-Centered

Relationships always connect domain objects.

Processes and events do not participate in the Interaction Model.

---

## Directional

Relationships are defined from one object toward another.

Direction expresses meaning, not implementation.

---

# Relationship Types

## belongs to

Represents contextual ownership.

Example:

Project → Area

---

## contains

Represents logical organization.

Example:

Area → Project

---

## references

Represents an explicit reference from one object to another.

A reference does not imply dependency or ownership.

Example:

Project → Resource

---

## supports

Represents knowledge or context provided by one object to another.

Support is conceptual rather than structural.

Example:

Resource → Project

---

# Domain Relationships

## Project

belongs to

- Area

contains

- Meeting

references

- Reference
- Resource
- Journal Entry

---

## Area

contains

- Project

---

## Meeting

supports

- Project

references

- Reference
- Resource

---

## Reference

supports

- Project
- Resource

---

## Resource

supports

- Project

references

- Reference

---

## Journal Entry

references

- Project
- Area
- Resource

---

# Scope

The Interaction Model defines only semantic relationships.

The following concepts are intentionally excluded:

- Cardinality
- Business rules
- Object lifecycles
- Workflows
- Events
- Implementation details

These belong to other architectural models.

---

# Relationship Overview

Execution

Project
    belongs to → Area
    contains → Meeting
    references → Reference
    references → Resource
    references → Journal Entry

Area
    contains → Project

Meeting
    supports → Project
    references → Reference
    references → Resource

Knowledge

Reference
    supports → Project
    supports → Resource

Resource
    supports → Project
    references → Reference

Thinking

Journal Entry
    references → Project
    references → Area
    references → Resource
