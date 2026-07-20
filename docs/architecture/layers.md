# Architecture Layers

Ohtli is organized into six architectural layers.

## Layer 1 — Filesystem

Defines how information is physically organized.

Responsibilities:

* Directory structure
* File organization
* Naming conventions

---

## Layer 2 — Metadata

Provides structured information about documents.

Responsibilities:

* YAML front matter
* Classification
* Status
* Relationships

---

## Layer 3 — Domain Model

Defines the concepts managed by Ohtli.

Examples:

* Project
* Area
* Knowledge
* Journal
* Review

---

## Layer 4 — Workflows

Defines how information moves through the system.

Examples:

* Capture
* Clarify
* Plan
* Execute
* Review
* Archive

---

## Layer 5 — Views

Defines how information is presented without changing its source.

Examples:

* Dashboards
* Task lists
* Reports
* Queries

Views never own data.

---

## Layer 6 — Automation

Implements repetitive processes.

Examples:

* Templates
* Scripts
* Plugin integrations
* AI assistants

Automation must never redefine the workflow. It only accelerates it.
