# ADR-0004: Adopt Actor-Neutral Automation

* **Status:** Accepted
* **Date:** 2026-08-21

## Context

Early ("M1 Core Specification") documentation at `docs/automation/automation-principles.md` asserted that Ohtli must keep "Human in Control" and that every automated process must have a manual alternative.

During Phase 7 (Automation Model, #85), a cross-check against the canonical Workflow and Execution Models found a direct contradiction: those models already treat Human, Deterministic System, AI-Assisted System, and Hybrid System as structurally equivalent Actors, with no actor holding special authority over another (`AI != Semantic Authority` applies to all actors equally, not as an AI-subordinate-to-human rule).

The project owner resolved this explicitly: Ohtli must be actor-neutral — operable both manually by a human and automatically by AI, without a mandated manual alternative or a human-superiority hierarchy.

## Decision

Ohtli adopts actor neutrality as a binding architectural principle.

Human, Deterministic System, AI-Assisted System, and Hybrid System are structurally equivalent Actors across the Workflow, Execution, User Experience, and Automation Models. No actor kind holds a special architectural authority over another.

AI is optional. Nothing in the canonical architecture may require AI participation, and nothing may require a human alternative to exist for a given Workflow or Automation.

The superseded principle — "Human in Control" and mandatory manual alternatives — is not carried forward. `docs/automation/automation-principles.md`, which asserted it, was deleted in #87 as part of reconciling superseded automation documentation.

## Alternatives Considered

* Keep "Human in Control" as a binding constraint on all Automation, requiring every automated Workflow to retain a manual initiation path.
* Introduce a formal actor hierarchy (Human > AI > Deterministic System) granting humans veto authority over automated Execution.

Both were rejected: they would require every future Automation or Execution definition to carry an additional, asymmetric authorization concept that the Workflow and Execution Models do not otherwise need, and they contradict the project owner's explicit intent for Ohtli to be usable identically by a human or by AI.

## Consequences

### Advantages

* One Actor contract applies uniformly across Workflow, Execution, User Experience, and Automation Models — no per-actor special case.
* Automation Model (Phase 7) requires no authorization or capability model beyond active/inactive control, since no actor-priority policy exists to enforce.
* Ohtli can be driven end-to-end by an AI-assisted or fully automated system without an architectural requirement for a parallel manual path.

### Trade-offs

* Any future Authorization Model that does want to constrain which actor kinds may initiate a given Workflow or Automation must introduce that constraint explicitly, as new architecture — it cannot rely on an implicit human-priority default.
* Documentation and tooling built against the earlier "Human in Control" principle (none currently exists beyond the deleted `docs/automation/automation-principles.md`) would need to be revisited if reintroduced.

## Related Decisions

None superseded directly; this decision formalizes a resolution reached during Phase 7 (#85, #87) that previously existed only in issue and pull request discussion.
