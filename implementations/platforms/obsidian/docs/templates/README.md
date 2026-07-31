# Template System

This directory documents the template system used by the Obsidian platform.

Templates implement the metadata model defined in the metadata documentation.

## Goals

- Keep templates consistent.
- Reuse common metadata.
- Minimize duplication.
- Support native Obsidian Properties.
- Separate documentation from implementation.

## Structure

| Directory | Description |
|-----------|-------------|
| templates/ | Executable templates |
| docs/templates/ | Template documentation |

## Design Principles

- Templates implement the metadata model.
- Templates are reusable.
- Every template represents one note type.
- Shared content should be centralized whenever possible.
