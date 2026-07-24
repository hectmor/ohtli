# Configuration Policy

This document defines how the Obsidian platform is configured.

The primary goal is reproducibility.

Every contributor should obtain the same initial experience after cloning the repository.

## Principles

### Shared Configuration

Shared configuration defines how the platform behaves.

Examples include:

- Enabled core plugins
- Default appearance
- Template configuration
- Graph configuration

Shared configuration is committed to Git.

---

### Personal Configuration

Personal configuration reflects an individual workflow.

Examples include:

- Workspace layout
- Open files
- Keyboard shortcuts
- Bookmarks

Personal configuration is never committed.

---

## Versioning Policy

| File | Versioned |
|------|-----------|
| app.json | Yes |
| appearance.json | Yes |
| core-plugins.json | Yes |
| graph.json | Yes |
| templates.json | Yes |
| workspace.json | No |
| workspace-mobile.json | No |
| hotkeys.json | No |
| bookmarks.json | No |

## Goals

- Portable
- Predictable
- Reproducible
- Easy to maintain

## Non Goals

The platform does not attempt to standardize personal productivity preferences.

Only behavior that benefits every user is shared.
