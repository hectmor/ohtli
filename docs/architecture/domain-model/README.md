# Domain Model

## Purpose

The Domain Model defines the conceptual entities that compose Ohtli.

It answers a single question:

> What exists inside Ohtli?

The Domain Model is independent of any editor, programming language,
database, or implementation.

It does not define workflows, events, or implementation details.

---

# Domain Object Definition

A domain object is a persistent conceptual entity that represents a
fundamental element of the system and possesses identity, purpose,
and meaning independently of its implementation.

A concept belongs to the Domain Model only if it satisfies all of the
following properties:

- Persistence
- Identity
- Purpose
- Independence

---

# Design Principles

## Objects over Notes

Ohtli is organized around domain objects, not notes.

Notes are one possible implementation.

---

## Technology Independent

The conceptual model must remain valid regardless of the implementation.

---

## Single Responsibility

Every object has one primary responsibility.

---

## Core Objects

### Execution

- Project
- Area
- Meeting

### Knowledge

- Reference
- Resource

### Thinking

- Journal Entry

---

# Deferred Concepts

The following concepts require further architectural evaluation and are
not part of the first version of the Domain Model.

- Task
- Goal

---

# Rejected Concepts

The following concepts belong to other architectural models.

- Review → Workflow Model
