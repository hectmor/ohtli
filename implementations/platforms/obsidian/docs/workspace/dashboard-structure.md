# Dashboard Structure

## Purpose

This document defines the canonical structure for all dashboards within the
Ohtli workspace.

Every dashboard should follow the same organization to provide a consistent
navigation experience.

---

# Structure

```text
Title

↓

Purpose

↓

Navigation

↓

Contents

↓

Related
```

---

## Title

The dashboard title identifies the vault section.

Examples:

- Workspace
- Projects
- Areas
- Knowledge
- Journal
- Reviews

---

## Purpose

A short description explaining the purpose of the section.

The purpose should answer:

> Why does this section exist?

---

## Navigation

Links to the most relevant dashboards.

Every dashboard must include a link back to the workspace.

---

## Contents

The main section.

This contains links to notes, indexes or instructions related to the section.

---

## Related

Links to closely related sections.

These links improve navigation without duplicating information.

---

## Design Principles

- Keep dashboards lightweight.
- Avoid dynamic content.
- Avoid plugin-specific functionality.
- Use only Markdown and wiki links.
- Keep navigation predictable.
- Minimize maintenance.

---

## Example

```markdown
# Projects

## Purpose

Projects represent finite efforts with a defined outcome.

---

## Navigation

- [[workspace]]

---

## Contents

- [[project-a]]
- [[project-b]]

---

## Related

- [[areas/index]]
- [[knowledge/index]]
```
