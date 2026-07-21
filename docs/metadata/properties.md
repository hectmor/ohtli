# Property Classification

Metadata properties are divided into two categories.

## Core Properties

Core Properties are common to every entity in the Ohtli framework.

These properties should be present in all templates.

| Property  | Description                           |
| --------- | ------------------------------------- |
| `title`   | Human-readable title of the document. |
| `type`    | Entity type.                          |
| `created` | Creation timestamp.                   |
| `updated` | Last modification timestamp.          |
| `tags`    | Classification tags.                  |

Example:

```yaml
---
title:
type:
created:
updated:
tags: []
---
```

## Entity-specific Properties

Entity-specific properties are used only when they provide meaningful information for a particular entity.

These properties are optional and should not be included in every template by default.

| Property  | Typical Usage         |
| --------- | --------------------- |
| `status`  | Projects, Reviews     |
| `aliases` | Knowledge             |
| `parent`  | Hierarchical entities |
| `related` | Cross references      |
| `owner`   | Shared workspaces     |

The goal is to keep templates simple while maintaining a consistent metadata model throughout the framework.
