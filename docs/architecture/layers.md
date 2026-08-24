# Architecture Layers

Ohtli is organized into six architectural layers.

The layers describe different levels of responsibility within the
system.

They do not represent a processing pipeline or mandatory execution
order.

Higher layers may operate on concepts established by lower layers, but
each layer preserves its own architectural responsibility.

## Layer 1 — Filesystem

Defines how information is physically organized.

The canonical definitions belong to:

- `filesystem-model/`

Responsibilities:

- Directory structure
- File organization
- Naming conventions

---

## Layer 2 — Metadata

Provides structured information about documents.

The canonical definitions belong to:

- `metadata-model/`

Responsibilities:

- YAML front matter
- Classification
- Status
- Relationships

Metadata represents structured information without redefining domain
semantics.

---

## Layer 3 — Domain Architecture

Defines the semantic concepts managed by Ohtli and the relationships
between them.

The canonical definitions belong to:

- `domain-model/`
- `interaction-model/`

The Domain Model defines what exists in Ohtli and what those concepts
mean.

The Interaction Model defines the semantic relationships between Domain
Objects.

This layer does not define workflows or events.

---

## Layer 4 — State and Transformation

Defines how Ohtli represents observable change and how relevant system
state may be transformed.

The canonical definitions belong to:

- `event-model/`
- `workflow-model/`
- `representation-model/`
- `execution-model/`

The Event Model preserves historical evidence of observable change.

The Representation Model defines how canonical semantics are represented
independent of implementation technology.

The Execution Model defines what it means for a Workflow to happen.

The Workflow Model defines six transformation classes:

- Capture — informational
- Processing — semantic
- Execution — operational
- Knowledge — epistemic
- Review — evaluative
- Archive — contextual

Workflows do not form a mandatory pipeline.

They become applicable according to relevant system state and context.

This layer does not prescribe a universal workflow sequence.

---

## Layer 5 — Views

Defines how information is presented without changing its source.

The canonical definitions belong to:

- `user-experience/`

Examples:

- Dashboards
- Task lists
- Reports
- Queries

Views never own data or redefine the architectural semantics of the
information they present.

---

## Layer 6 — Automation

Implements or assists repetitive and operational processes.

The canonical definitions belong to:

- `automation-model/`

Examples:

- Templates
- Scripts
- Plugin integrations
- AI assistants

Automation must not redefine architectural semantics.

It may execute or assist operations defined by lower architectural
layers while preserving their contracts and invariants.
