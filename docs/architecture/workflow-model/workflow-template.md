# Workflow Name

## Purpose

Describe why this workflow exists.

A workflow must have one primary responsibility.

It should answer:

> Why does this workflow exist?

---

## Input

Describe the information or domain objects that enter the workflow.

The input should describe conceptual information rather than
implementation details.

Examples:

- External information
- Project
- Resource
- Journal Entry

---

## Output

Describe what the workflow produces.

Outputs may include:

- Updated domain objects
- New relationships
- Events
- Persistent information

Outputs never redefine the Domain Model.

---

## Preconditions

Describe what must already be true before the workflow can begin.

Examples:

- Information exists outside the system.
- A project already exists.
- A meeting has been recorded.

---

## Postconditions

Describe what must be true after the workflow completes.

Examples:

- Information has been preserved.
- The project has been archived.
- A relationship has been established.

---

## Invariants

Describe rules that must remain true throughout the workflow.

These rules may never be violated.

Examples:

- Capture never classifies information.
- Events are never modified.
- Objects keep their identity.

---

## Guarantees

Describe what the workflow promises if it completes successfully.

Examples:

- Information cannot be lost.
- Objects remain consistent.
- History is preserved.

---

## Flow

Describe the conceptual sequence of the workflow.

The flow should focus on conceptual transformations rather than
implementation.

Example:

Information

↓

Capture

↓

Persistent Information

↓

Processing

---

## Related Domain Objects

List the domain objects that participate in the workflow.

Example:

- Project
- Resource
- Journal Entry

---

## Generated Events

List the observable events that may be produced.

Example:

- Information Captured
- Resource Linked
- Project Archived

---

## Next Workflows

Describe which workflows may continue after this one.

A workflow may have multiple successors.

Example:

- Processing Workflow
- Archive Workflow

---

## Notes

Optional section for architectural observations,
assumptions, or future considerations.

This section must not redefine the workflow.
