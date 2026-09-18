# Journal Entry Metadata

Journal entries capture thoughts associated with a specific moment in
time.

A Journal Entry is distinct from a daily note (`daily-note.md`,
`note_type: daily_note`): the daily note is the UX surface driven by
the Obsidian Daily Notes plugin, and this schema does not replace or
migrate it.

## Inherits

- Common Metadata

## Properties

| Property | Type | Required |
|----------|------|----------|
| id | Text | Yes |
| status | Select | Yes |
| context | Select | Yes |

`id` is a stable identifier assigned at Capture. It exists so that
identity survives rename and relocation, per the canonical
Representation Model (`Rename != Identity change`, `Relocation !=
Identity change`). It is not derived from the title or filename and
must not be recomputed if either changes.

`context` is independent from `status`. It represents contextual
presence (operational vs. historical), set by the Archive workflow,
not lifecycle. Per `archive-workflow.md`'s Lifecycle Independence
invariant, Archive/Reactivate must never change `status`.

The Domain Model's Essential Attribute `Date` maps to the common
`created` property rather than a separate property (see "Avoid
duplicated information" in the metadata README). Known limitation:
`created` is the Capture-time date, so a backdated entry's `created`
differs from the moment in its title.

## Status values

- created

## Context values

- operational
- historical
