# Template Structure

This document defines the canonical structure for every template used by the
Ohtli Obsidian platform.

Templates implement the metadata model defined in
`docs/metadata/` and provide a consistent authoring experience across all
note types.

---

# Canonical Structure

Every template follows the same logical structure.

```text
Properties
↓
Title
↓
Overview (optional)
↓
Structured Sections
↓
User Content
```

The logical structure is independent of the underlying implementation.

Obsidian stores Properties as YAML frontmatter. This storage format is an
implementation detail and is not part of the template specification.

---

# 1. Properties

Properties implement the metadata model.

## Rules

- Properties are always the first element of a note.
- Only properties defined in `property-types.md` are allowed.
- Property names must exactly match the metadata specification.
- Properties must follow the canonical order.
- Universal properties always precede note-specific properties.

Properties are expected to be managed through the native Obsidian interface.

---

# 2. Title

Every template defines a single level-one heading.

```markdown
# <% tp.file.title %>
```

## Rules

- The title must match the filename.
- Only one level-one heading is allowed.

---

# 3. Overview

The overview provides a short introduction to the note.

Examples include:

- Objective
- Description
- Summary

## Rules

- This section is optional.
- Keep the content concise.
- Do not duplicate metadata.

---

# 4. Structured Sections

Templates organize information into logical sections.

## Rules

- Use ATX headings.
- Main sections use `##`.
- Subsections use `###` only when necessary.
- Prefer short and reusable section names.
- Maintain a logical reading order.

---

# 5. User Content

Templates provide structure.

Users provide content.

Templates should avoid unnecessary placeholder text and should never contain
example data intended to be deleted.

---

# Property Order

Universal properties always appear before note-specific properties.

Canonical order:

```text
note_type

created
updated

tags
aliases

...note-specific properties...
```

---

# Heading Hierarchy

| Level | Usage |
|------|-------|
| # | Note title |
| ## | Main section |
| ### | Subsection |

Avoid deeper heading levels unless there is a clear need.

---

# Templater

Templates may use the Templater plugin to generate dynamic values.

Typical use cases include:

- Current date
- Current time
- File title

Templater is responsible only for generating dynamic content.

Business rules belong to the metadata model.

---

# Design Principles

- Templates implement the metadata model.
- Templates are self-contained.
- Templates prioritize readability.
- Templates minimize duplication.
- Templates remain portable Markdown documents.
- Native Obsidian features are preferred over custom logic.
- Every template follows the same structure.
