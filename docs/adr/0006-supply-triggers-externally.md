# ADR-0006: Supply Automation Triggers Externally

* **Status:** Accepted
* **Date:** 2026-09-24

## Context

The Automation Model defines a Trigger as a conceptual signal that starts an evaluation, and deliberately defines no mechanism for it: it does not define schedulers, cron, queues, workers, agents or any implementation technology, and it "is complete without a scheduling technology or AI" (`docs/architecture/automation-model/README.md`, Architectural Boundaries).

Evaluating a Trigger produces an Execution Request only if the Automation is active, its own Automation Conditions hold, and the Workflow is applicable. A Trigger occurring does not guarantee an Execution Request, and an Automation Condition never overrides Workflow Applicability (`docs/architecture/automation-model/automation-triggers-and-conditions.md`; `automation-foundations.md`).

In the code, only Workflow Applicability exists today: `execute_capture` and `execute_processing` check it before doing anything. There is no Automation entity and no trigger source anywhere under `src/ohtli`, and no code branches on the Actor (ADR-0004).

Without a rule for how a Trigger reaches Ohtli, each script or integration decides for itself. The two example trigger scripts did, and by default they wrote to the real vault (fixed in #149).

## Decision

Ohtli does not acquire a trigger source of its own: no daemon, file-watcher, cron integration, scheduler or new dependency.

A Trigger is something outside Ohtli invoking an Ohtli entry point: a person, cron, systemd, an AI agent, or another script.

Of the conditions that must hold before a Trigger yields an Execution Request, the invoker's configuration owns the first ones: that the Automation is active, that this Trigger belongs to it, and its Automation Condition. Ohtli always enforces the last one, Workflow Applicability, and always records the Actor it was given in the Event.

The Actor is attribution, not authentication or authorization. Nothing prevents an invoker from declaring itself `human`, so the Actor must not be used as access control.

Every automated entry point must declare which Actor it is and must target an explicitly chosen vault, never a default one.

## Alternatives Considered

* A built-in scheduler or daemon inside Ohtli. Rejected: it adds a dependency and runtime state, and contradicts the Automation Model's architectural boundaries.
* An Obsidian plugin or file-watcher as the trigger source. Rejected: it ties Ohtli to one platform.
* Storing Automation definitions in the vault and evaluating them inside Ohtli. Deferred: nothing needs it yet.

## Consequences

### Advantages

* No new dependency and no runtime state to manage.
* Consistent with ADR-0004 (actor-neutral) and ADR-0005 (Python and Obsidian as primary implementation): a human, cron and an AI agent are invoked the same way.
* Every entry point stays testable against a temporary vault.

### Trade-offs

* Ohtli keeps no Automation history: the invoker owns scheduling, retries and deduplication.
* Attribution depends on the invoker declaring its Actor honestly.
* The CLI needs a way to declare a non-human Actor; it currently records every command as `human`. This is left to a follow-up (Phase 37c).

## Related Decisions

* ADR-0004: Adopt Actor-Neutral Automation.
* ADR-0005: Adopt Python and Obsidian as Primary Implementation.
