# System Architecture

## Purpose

The System Architecture defines how the conceptual models of Ohtli work
together to form a coherent system.

It answers a single question:

> How does Ohtli work as a whole?

The System Architecture does not redefine the Domain Model,
Interaction Model, Event Model, or Workflow Model.

Instead, it establishes their responsibilities, boundaries,
and interactions.

---

# Architectural Principles

The architecture of Ohtli is based on four fundamental principles.

## Objects are persistent

Objects represent stable concepts within the system.

They exist independently of any implementation technology.

---

## Processes transform objects

Workflows operate on domain objects.

Processes may create, modify, relate, or archive objects.

Processes are not domain objects.

---

## Events record facts

Events are immutable records describing observable facts that occurred
within the system.

Events never represent intentions or future actions.

---

## Views visualize models

Views present information without owning it.

A view never modifies the conceptual architecture.

---

# Architectural Layers

Ohtli is organized into four conceptual layers.

## Thinking

Supports idea generation and personal reflection.

Primary object:

- Journal Entry

---

## Knowledge

Represents information and understanding.

Primary objects:

- Reference
- Resource

---

## Execution

Represents work and responsibilities.

Primary objects:

- Area
- Project
- Meeting

---

## History

Represents the observable history of the system.

Primary model:

- Event Model

---

# Core Models

## Domain Model

Defines what exists.

The Domain Model specifies the persistent conceptual objects of Ohtli.

---

## Interaction Model

Defines how domain objects relate to one another.

Relationships are semantic and technology independent.

---

## Event Model

Defines observable facts that occur within the system.

Events describe history.

---

## Workflow Model

Defines how work moves through the system.

Workflows describe behavior rather than structure.

---

# System Views

Views expose information from one or more conceptual models.

Views never introduce new concepts.

Examples include:

- Workspace
- Timeline
- Dashboards
- Indexes

---

# Design Rules

The following architectural rules apply throughout the system.

## Separation of Concerns

Objects, relationships, processes, events, and views have distinct
responsibilities.

---

## Technology Independence

The conceptual architecture must remain valid regardless of its
implementation.

---

## Explicit Semantics

Objects and relationships always have explicit meaning.

Generic concepts should be avoided.

---

## Single Responsibility

Every conceptual element has one primary responsibility.

---

## Immutability of Events

Events are historical records and therefore immutable.

---

# Architectural Boundaries

The following belong to the conceptual architecture.

- Domain Model
- Interaction Model
- Event Model
- Workflow Model
- Views

The following belong to implementation.

- Obsidian
- Markdown
- Properties
- Templates
- Plugins
- Scripts
- Databases

Implementation choices must never redefine the conceptual architecture.

---

# Conceptual Overview

The architecture of Ohtli can be summarized as four complementary models.

Question                     Model

What exists?                 Domain Model

How are objects related?     Interaction Model

What happened?               Event Model

How does work flow?          Workflow Model

Together these models define the complete conceptual architecture of
Ohtli.

Every implementation must preserve this architecture.
