# ADR-0005: Adopt Python and Obsidian as Primary Implementation

* **Status:** Accepted
* **Date:** 2026-08-25

## Context

By Phase 8 (#90), the canonical architecture (Domain, Interaction,
Event, Workflow, Representation, User Experience, Execution,
Automation, Filesystem, Metadata Models) was complete and internally
consistent, but no implementation existed. The repository already
contained two pre-canonical, de facto implementations —
`implementations/reference/` and the project owner's live, git-tracked
Obsidian vault at `implementations/platforms/obsidian/vault/` — neither
built against the canonical models.

An implementation requires a concrete language and a concrete target
platform. The canonical models are deliberately technology-independent
and must remain so; selecting a language and a platform is an
implementation decision, not an architectural one, but it still needs
to be recorded so future work does not silently assume, or silently
contradict, the choice.

## Decision

Ohtli's primary implementation will be written in Python and will
target Obsidian as its primary platform.

```text
Python (language choice)   != Architecture
Obsidian (platform choice) != Architecture
```

The canonical models remain valid independent of this choice. Nothing
in the Domain, Interaction, Event, Workflow, Representation, User
Experience, Execution, Automation, Filesystem, or Metadata Models may
be defined in terms of Python or Obsidian. A future implementation
targeting a different language or platform remains conceptually valid
under the same canonical models.

Obsidian is one possible Filesystem Model medium and one possible
Representation Model surface (per `filesystem-model/README.md` and
`representation-model/README.md`) — not a redefinition of either.

## Alternatives Considered

* Defer the language/platform decision until Phase 9 work is complete,
  keeping Implementation Boundaries purely abstract. Rejected: the
  project owner already has a live, in-use Obsidian vault and a stated
  intent to build in Python; deferring the decision would not change
  the outcome, only delay recording it.
* Design Implementation Boundaries generically enough to support
  multiple simultaneous target platforms from the start. Rejected as
  premature per the project's Simplicity and Incremental Evolution
  principles — no second platform exists or is planned.

## Consequences

### Advantages

* Implementation work has a concrete, recorded target, unblocking
  Implementation Boundaries (Phase 9) and any future vertical slice.
* The existing Obsidian vault and reference implementation can be
  evaluated and reconciled against a known target rather than an
  open-ended one.

### Trade-offs

* Any future implementation targeting a different language or platform
  must be evaluated independently against the canonical models; this
  decision does not generalize automatically.
* Implementation-level documentation (Phase 9 onward) will reference
  Python and Obsidian concretely; care is required to keep that
  documentation separate from the technology-independent canonical
  models.

## Related Decisions

None superseded. This decision is scoped entirely to the implementation
layer defined in `docs/architecture/implementation/README.md` and does
not modify any canonical model.
