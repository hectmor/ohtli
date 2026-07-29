# Template Implementation

This document describes how the Ohtli template system is implemented in
Obsidian.

The implementation follows the template specification defined in
`template-structure.md`.

---

# Objectives

The implementation should:

- Follow the metadata model.
- Minimize custom logic.
- Prefer native Obsidian functionality.
- Use Templater only where dynamic content is required.

---

# Components

The template system consists of:

- Obsidian Templates
- Templater
- Native Properties

Each component has a specific responsibility.

---

# Responsibilities

## Metadata

Implemented using native Obsidian Properties.

## Dynamic Content

Implemented using Templater.

Examples include:

- Current date
- Current time
- File title

## Content Structure

Implemented using Markdown.

---

# Templater Usage

Templater should only be used for values that cannot be known beforehand.

Typical examples:

- Current date
- Current time
- Current year
- Current month
- Current file title

Templates should avoid complex scripting.

Business rules do not belong in Templater.

---

# Native Obsidian Features

Whenever possible, prefer native Obsidian features over custom logic.

Examples:

- Properties
- Daily Notes
- Templates
- Bases

---

# Folder Structure

Template files are stored in

```text
implementations/platforms/obsidian/templates/
```

Documentation is stored in

```text
implementations/platforms/obsidian/docs/templates/
```

---

# Design Principles

- Keep templates self-contained.
- Keep templates readable.
- Keep templates portable.
- Prefer declarative templates.
- Avoid unnecessary scripting.emplates should contain as little logic as possible.
