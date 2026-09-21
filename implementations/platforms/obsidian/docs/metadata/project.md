# Project Metadata

Projects represent work with a defined objective.

## Inherits

- Common Metadata

## Properties

| Property | Type | Required |
|----------|------|----------|
| id | Text | Yes |
| status | Select | Yes |
| context | Select | Yes |
| owner | Text | No |
| priority | Select | No |
| due | Date | No |
| relationships | List | No |

`id` is a stable identifier assigned at Capture. It exists so that
identity survives rename and relocation, per the canonical
Representation Model (`Rename != Identity change`, `Relocation !=
Identity change`). It is not derived from the title or filename and
must not be recomputed if either changes.

`context` is independent from `status`. It represents contextual
presence (operational vs. historical), set by the Archive workflow,
not lifecycle. Per `archive-workflow.md`'s Lifecycle Independence
invariant, Archive/Reactivate must never change `status`.

`relationships` is the Project's Current Relationship Set: a list of
Relationship Instances, **absent until the first link** (a note that was
never linked has no such key — Relationship Absence is not a
Relationship State). Its authority is the canonical **Interaction
Model**, not this metadata schema: metadata creates no relationship
meaning, direction, or cardinality (`metadata-model/README.md`). This
document only records how the canonical relationship `Project belongs to
Area (0..1)` is stored.

Each entry has:

| Key | Meaning |
|-----|---------|
| `id` | The relationship instance's own identity (not the identity of either object). |
| `type` | The canonical relationship type, verbatim: `belongs to`. |
| `target_id` | The target's stable `id`. **The authority.** |
| `target_type` | The target's kind: `area`. |
| `target_link` | A display-only, folder-qualified wikilink, e.g. `[[areas/health\|Health]]`. Non-authoritative decoration: nothing reads it back, it can go stale if the Area is renamed outside Obsidian, and removing it loses no information. |

Relationships reference the target by `id`, never by title or path
(`representation-invariants.md`, "Stable Relationship References"), so
renaming or relocating the Area needs no handling. The relationship is
stored on the Project only; the inverse (`Area contains Project`) is a
separate canonical relationship and is not stored. Linking never changes
`status` or `context`. It is established and removed through the
Processing workflow's `Relate` operation.

## Status values

- inbox
- planned
- active
- on_hold
- completed

## Context values

- operational
- historical

## Priority values

- low
- medium
- high
- critical
