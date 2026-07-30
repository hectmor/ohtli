# Domain Model

## Purpose

The domain model defines the conceptual objects that compose Ohtli.

These objects represent stable concepts independent of any software,
editor, storage format, or implementation.

The domain model answers one question:

> What exists inside Ohtli?

It intentionally does not define workflows, interactions, events,
or implementation details.

---

# Design Principles

## Objects over Notes

Ohtli is not organized around notes.

Every piece of information belongs to a domain object.

Notes are only one possible implementation.

---

## Stable Concepts

Objects represent concepts that remain stable over time.

Their implementation may evolve without changing the conceptual model.

---

## Single Responsibility

Every object has one primary responsibility.

Objects should not overlap in purpose.

---

## Technology Independent

The domain model must be implementable in any platform.

Obsidian is only one implementation.

---

# Core Objects

The first version of Ohtli defines the following domain objects.

- Project
- Area
- Meeting
- Reference
- Resource
- Review
- Journal Entry

---

# Project

## Purpose

Deliver a finite outcome.

A project exists to achieve a specific objective that has a clear end.

## Responsibilities

- Define an objective.
- Track progress.
- Organize work.
- Produce outcomes.

## Identity

A project has its own identity regardless of where it is stored.

## Lifecycle

- Created
- Active
- On Hold
- Completed
- Archived

---

# Area

## Purpose

Represent an ongoing responsibility.

Areas never have a defined end date.

## Responsibilities

- Maintain continuity.
- Group related projects.
- Define long-term ownership.

## Lifecycle

- Active
- Archived

---

# Meeting

## Purpose

Capture the outcome of a conversation.

A meeting records decisions, agreements, and action items.

## Responsibilities

- Record participants.
- Record decisions.
- Record action items.

## Lifecycle

- Recorded
- Archived

---

# Reference

## Purpose

Store external information.

References preserve original information without interpretation.

Examples include:

- Books
- Articles
- Videos
- Papers
- Websites
- Documentation

## Responsibilities

- Preserve sources.
- Support knowledge creation.

## Lifecycle

- Captured
- Archived

---

# Resource

## Purpose

Represent synthesized knowledge.

Resources are created from learning, analysis, or experience.

Unlike references, resources express understanding.

Examples include:

- Documentation
- Notes
- Guides
- Tutorials
- Research summaries

## Responsibilities

- Organize knowledge.
- Explain concepts.
- Support projects and areas.

## Lifecycle

- Draft
- Published
- Archived

---

# Review

## Purpose

Evaluate the state of the system.

Reviews ensure that projects, areas, and knowledge remain healthy.

## Responsibilities

- Evaluate progress.
- Identify improvements.
- Trigger decisions.

## Lifecycle

- Planned
- Completed

---

# Journal Entry

## Purpose

Support personal thinking.

Journal entries are free-form reflections.

They are not intended to organize work.

## Responsibilities

- Capture thoughts.
- Capture ideas.
- Capture reflections.

## Lifecycle

Immutable after creation.

---

# Object Summary

| Object | Purpose |
|----------|----------|
| Project | Deliver a finite outcome |
| Area | Maintain long-term responsibility |
| Meeting | Record conversations and decisions |
| Reference | Preserve external information |
| Resource | Represent synthesized knowledge |
| Review | Evaluate the system |
| Journal Entry | Support thinking |
