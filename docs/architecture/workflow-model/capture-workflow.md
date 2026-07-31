# Capture Workflow

## Purpose

Move information from outside Ohtli into a persistent state without
interpreting, classifying, or organizing it.

The Capture Workflow is the unique entry point through which information
enters the system.

It answers a single question:

> How does information enter Ohtli?

---

# Definition

Capture is the process of preserving information before any decision
about its meaning is made.

Capture transforms ephemeral information into persistent information.

It does not create domain objects.

It does not classify information.

It does not establish relationships.

---

# Input

Ephemeral information originating outside the system.

Examples include:

- Observation
- Idea
- Knowledge
- Commitment
- Reflection

The origin of the information is irrelevant.

---

# Output

Persistent information that belongs to Ohtli.

The information is available for future processing but has not yet been
assigned any semantic meaning.

---

# Preconditions

- Information exists outside Ohtli.
- Information has not yet been preserved.

---

# Postconditions

- Information belongs to Ohtli.
- Information cannot be lost.
- Information is available for processing.

---

# Invariants

The following rules are always true during Capture.

- No classification.
- No interpretation.
- No domain objects are created.
- No relationships are established.
- No workflow decisions are made.

---

# Guarantees

If Capture completes successfully:

- Information is preserved.
- Information is recoverable.
- Information is available for processing.
- Information remains independent of any domain object.

---

# Flow

Ephemeral Information

↓

Receive

↓

Persist

↓

Expose

↓

Persistent Information

---

# Related Domain Objects

None.

Capture operates before information becomes a domain object.

---

# Generated Events

- Information Captured

---

# Next Workflows

None.

Capture is responsible only for preserving information.

It does not decide which workflow should execute next.

Subsequent workflows operate based on the current state of the system.

---

# Architectural Principles

## Single Entry Point

All information enters Ohtli through the Capture Workflow.

---

## Preserve Before Meaning

Information is preserved before being interpreted.

---

## Zero Classification

Capture never classifies information.

---

## Zero Decision

Capture never makes domain decisions.

---

## Boundary Workflow

Capture is the only workflow whose input originates outside the system.

---

## State-Based Coordination

Capture does not invoke other workflows.

Workflows are coordinated through the state of the system rather than
through direct dependencies.

---

# Summary

The Capture Workflow introduces information into Ohtli while minimizing
friction and preserving architectural independence.

Its only responsibility is to transform information from an ephemeral
state into a persistent state.

Meaning is introduced later by the Processing Workflow.
