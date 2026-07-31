# Event Model

## Purpose

The Event Model defines the observable facts that may occur within Ohtli.

It answers a single question:

> What happened?

Events are immutable historical records that describe changes affecting
one or more domain objects.

The Event Model does not define workflows, user actions, or
implementation details.

---

# Event Definition

An event is an immutable record that describes a completed fact affecting
the state or relationships of one or more domain objects.

Every event satisfies the following properties:

- Immutable
- Historical
- Object-Centered
- Observable

---

# Design Principles

## Immutable

Events never change once recorded.

---

## Historical

Events always describe completed facts.

---

## Object-Centered

Every event affects one or more domain objects.

---

## Observable

Only observable facts become events.

Intentions and plans are not events.

---

# Event Categories

## Object Events

Describe changes affecting a single domain object.

Examples

- Project Created
- Project Archived
- Area Created
- Resource Published
- Journal Entry Created

---

## Relationship Events

Describe changes in relationships between objects.

Examples

- Resource Linked to Project
- Reference Attached to Resource
- Meeting Associated with Project

---

## Knowledge Events

Describe the evolution of knowledge.

Examples

- Reference Captured
- Resource Published
- Resource Updated

---

## Thinking Events

Describe thinking artifacts.

Examples

- Journal Entry Created

---

# Timeline

The Timeline is a chronological view of system events.

It is a visualization of the Event Model rather than an independent
domain object.

---

# Non-Events

The following concepts are processes and therefore do not belong to the
Event Model.

- Capture
- Archive
- Weekly Review
- Process Inbox
- Create Project

These belong to the Workflow Model.
