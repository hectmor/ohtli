# Area Metadata

Areas represent ongoing responsibilities.

## Inherits

- Common Metadata

## Properties

| Property | Type | Required |
|----------|------|----------|
| id | Text | Yes |
| status | Select | Yes |
| context | Select | Yes |
| owner | Text | No |
| review_frequency | Select | No |

`id` is a stable identifier assigned at Capture. It exists so that
identity survives rename and relocation, per the canonical
Representation Model (`Rename != Identity change`, `Relocation !=
Identity change`). It is not derived from the title or filename and
must not be recomputed if either changes.

`context` is independent from `status`. It represents contextual
presence (operational vs. historical), set by the Archive workflow,
not lifecycle. Per `archive-workflow.md`'s Lifecycle Independence
invariant, Archive/Reactivate must never change `status`.

An Area has **no** `relationships` property. `Area contains Project (0..*)`
is the complement of `Project belongs to Area (0..1)`, which the Interaction
Model ("Relationship Semantics and Inverses") calls semantically
complementary and does not require to be a separate stored relationship.
This implementation therefore derives it: the Projects an Area contains are
the Projects whose `belongs to` targets this Area's `id`. Nothing is written
to the Area, so the view cannot go stale or contradict the Project side, and
it cannot be established from the Area (`ohtli link --from-type area ...` is
refused and points to the Project side). Read it with `ohtli contains
<area>`; archived (historical) Projects are included, marked as such,
because Archive does not cascade.

## Status values

- active

## Context values

- operational
- historical
