# Entity Relationships

This document describes the conceptual relationships between the entities of Ohtli.

## High-Level Structure

```text
Inbox
    │
    ▼
Project ───────────────┐
    │                  │
    ├── Journal        │
    ├── Knowledge      │
    └── Attachments    │
                       │
Area ──────────────────┘
    │
    └── Reviews

Knowledge
    └── Supports Projects and Areas

Templates
    └── Standardize all entities

Dashboards
    └── Present information without owning it
```

## Relationship Principles

### Inbox

The Inbox is the entry point to the framework.

Information remains in the Inbox only until it is processed.

---

### Projects

Projects belong to an Area.

Projects may reference Knowledge, Journals, and Attachments.

---

### Areas

Areas group related Projects and are periodically evaluated through Reviews.

---

### Knowledge

Knowledge supports multiple Projects and Areas.

It is never owned by a single Project.

---

### Journals

Journals record the history of Projects or Areas.

---

### Reviews

Reviews evaluate Projects, Areas, or the framework itself.

---

### Templates

Templates define the structure of entities but are not entities themselves.

---

### Dashboards

Dashboards aggregate and present information from multiple entities.

They never modify or own the underlying data.
