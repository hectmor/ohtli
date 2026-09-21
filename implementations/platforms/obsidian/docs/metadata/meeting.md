# Meeting Metadata

Meeting notes document conversations and decisions.

## Inherits

- Common Metadata

## Properties

| Property | Type | Required |
|----------|------|----------|
| id | Text | Yes |
| status | Select | Yes |
| context | Select | Yes |
| attendees | List | No |
| meeting_date | Date | Yes |
| location | Text | No |
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

`relationships` is the Meeting's Current Relationship Set: a list of
Relationship Instances, **absent until the first link**. Its authority is
the canonical **Interaction Model**, not this metadata schema. This
document only records which implemented relationships this note type
holds as a **source**: `Meeting references Reference (0..*)`,
`Meeting references Resource (0..*)`, and `Meeting supports Project (0..1)`.
The last is bounded: a Meeting supports at most one Project, so a second
link is refused, and it may be unlinked without naming the Project.
Instance fields, identity, uniqueness, and unlink rules are the same for
every source type and are described once in `project.md`
("`relationships`").

`Project contains Meeting (0..*)` is stored on the **Project**, not on the
Meeting. It is independent of `Meeting supports Project`: the two may name
different Projects.

## Status values

- recorded

## Context values

- operational
- historical
