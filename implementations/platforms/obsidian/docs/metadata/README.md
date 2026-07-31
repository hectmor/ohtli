# Metadata Model

This directory defines the metadata model for the Ohtli Obsidian platform.

## Objectives

- Provide a consistent metadata schema.
- Use native Obsidian Properties.
- Enable filtering and visualization through Bases.
- Keep Markdown portable and human-readable.

## Metadata hierarchy

Every note inherits the common metadata.

Additional properties depend on the note type.

```
Common
├── Daily Note
├── Project
├── Area
├── Resource
├── Meeting
└── Reference
```

## Naming conventions

- Property names use `snake_case`.
- Dates follow ISO 8601 (`YYYY-MM-DD`).
- Property names should remain stable.
- Avoid duplicated information.


