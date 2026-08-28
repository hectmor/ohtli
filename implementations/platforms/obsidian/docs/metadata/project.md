# Project Metadata

Projects represent work with a defined objective.

## Inherits

- Common Metadata

## Properties

| Property | Type | Required |
|----------|------|----------|
| id | Text | Yes |
| status | Select | Yes |
| owner | Text | No |
| priority | Select | No |
| due | Date | No |

`id` is a stable identifier assigned at Capture. It exists so that
identity survives rename and relocation, per the canonical
Representation Model (`Rename != Identity change`, `Relocation !=
Identity change`). It is not derived from the title or filename and
must not be recomputed if either changes.

## Status values

- inbox
- planned
- active
- on_hold
- completed
- archived

## Priority values

- low
- medium
- high
- critical
