# Standard Properties

This document defines the standard metadata properties used by Ohtli.

| Property  | Required | Description                                |
| --------- | -------- | ------------------------------------------ |
| `title`   | Yes      | Human-readable document title.             |
| `type`    | Yes      | Domain entity represented by the document. |
| `status`  | No       | Current lifecycle state.                   |
| `created` | Yes      | Creation date (ISO 8601).                  |
| `updated` | Yes      | Last modification date (ISO 8601).         |
| `tags`    | No       | Classification keywords.                   |
| `aliases` | No       | Alternative names.                         |
| `parent`  | No       | Parent entity.                             |
| `related` | No       | Related documents.                         |
| `owner`   | No       | Responsible person or team.                |

## Design Principles

* Every property has a single responsibility.
* Properties must have consistent meaning across all document types.
* Prefer reusable properties over entity-specific ones.
* New properties should be introduced only when they provide value across multiple entities.
* Metadata should remain stable over time.
