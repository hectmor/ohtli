# Contributing

Thank you for contributing to Ohtli.

The goal of this document is to define the project's development standards and ensure consistency as the framework evolves.

## General Principles

* English is the official language of the project.
* Keep the framework tool-independent whenever possible.
* Favor simplicity over complexity.
* Document significant architectural decisions using ADRs.
* Leave the project in a consistent state after every commit.

## Naming Conventions

### Files and Directories

Use **kebab-case** for all file and directory names.

Example:

```text
execution-system.md
project-template.md
plugin-architecture.md
```

### Markdown

* Use ATX headings (`#`).
* Use relative links.
* Keep documents concise and focused.
* Each document should answer a single question.

## Git Workflow

### Commit Messages

Ohtli follows the Conventional Commits specification.

Examples:

```text
docs: add initial project README
feat: introduce architecture decision records
fix: clarify project lifecycle
refactor: simplify execution workflow
```

### Commit Policy

* One commit represents one complete feature or one cohesive change.
* A commit may modify multiple files if they belong to the same feature.
* Avoid partial implementations.
* Every commit must leave the repository in a working and consistent state.

## Architecture Decisions

Significant architectural decisions must be documented as ADRs.

New ADRs should:

* Use sequential numbering.
* Never modify the historical meaning of accepted ADRs.
* Supersede previous ADRs when necessary.

## Documentation

Documentation should explain:

* Why a decision exists.
* What problem it solves.
* How it fits into the framework.

Avoid documenting implementation details unless necessary.

