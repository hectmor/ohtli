# Review Workflow

## Purpose

Evaluate relevant system state in order to determine what deserves
deliberate attention.

Review examines current state, relevant expectations, historical
context, and observable changes within a defined scope.

It answers:

> What requires attention?

Review evaluates significance.

It does not prescribe the response, perform operational work, develop
understanding, execute lifecycle transitions, or archive domain objects.

---

# Definition

Review is the workflow through which relevant system state is observed
and evaluated in context.

The workflow transforms:

Relevant System State

↓

Review Assessment

A Review Assessment makes the significance of the observed state
explicit within the scope of the Review.

Review may identify that:

- something requires attention;
- nothing currently requires attention;
- the available information is insufficient for a responsible
  assessment.

Review does not require a problem to exist.

Attention means that something deserves deliberate consideration.

---

# Input

Review operates on system state relevant to a defined scope.

Relevant information may include:

- current domain state;
- Projects;
- Areas;
- References;
- Resources;
- Meetings;
- Journal Entries;
- persistent information;
- execution results;
- developed understanding;
- relevant Events;
- historical state;
- outcomes;
- responsibilities;
- desired states;
- constraints;
- previous assessments.

Not every Review must inspect every part of Ohtli.

The scope determines what information is relevant.

---

# Output

Review Assessment.

A Review Assessment represents the evaluation produced for the current
scope and context.

It may indicate that:

- attention is required;
- no attention is currently required;
- there is insufficient basis for a responsible evaluation.

The Assessment should preserve the conceptual basis for its evaluation.

A Review Assessment is not automatically a domain object.

---

# Scope

Every Review has a conceptual scope.

Scope answers:

> What is being reviewed?

Examples include:

- a Project;
- an Area;
- a set of Projects;
- a set of Areas;
- unresolved information;
- a relevant subset of the system;
- the whole system.

Review evaluates only the state relevant to its scope.

A Review does not need to inspect the entire system.

---

# Temporal Context

A Review may also have a temporal context.

Temporal context answers:

> Over what relevant period is the state being evaluated?

Examples include:

- today;
- this week;
- since the previous Review;
- the last month;
- the entire relevant history.

Scope and temporal context are independent concepts.

For example, a weekly system Review may be represented conceptually as:

Review

scope:
relevant system state

temporal context:
since previous weekly review

Review is not inherently periodic.

It may occur periodically, on demand, or whenever evaluation becomes
relevant.

---

# Triggers

Review may begin when there is an intention to evaluate a defined scope.

Possible triggers include:

- a periodic review practice;
- an explicit decision to review a Project or Area;
- meaningful changes in system state;
- completion of significant operational work;
- uncertainty about the current state;
- a need to reconsider relevance or lifecycle state.

A trigger makes Review applicable.

Review does not require a scheduled cadence.

---

# Preconditions

- A scope is defined.
- There is an intention to evaluate that scope.

Complete or sufficient information is not required before Review begins.

Insufficient information may itself become part of the resulting
Assessment.

---

# Postconditions

When a Review instance completes:

- relevant state within the scope has been observed;
- available context has been considered;
- a Review Assessment has been produced;
- relevant attention has been surfaced when appropriate;
- insufficient basis has been made explicit when responsible evaluation
  was not possible.

Review completion does not imply that:

- a problem has been solved;
- an action has been selected;
- operational work has been performed;
- a lifecycle transition has occurred;
- knowledge has been developed;
- an object has been archived.

---

# Invariants

The following rules must remain true throughout Review.

## Scope-Bounded

Review evaluates only state relevant to its defined scope.

A system-wide Review and a Project Review use the same workflow with
different scopes.

---

## Context-Aware

Review may evaluate current state using relevant context such as:

- outcomes;
- responsibilities;
- desired states;
- constraints;
- previous state;
- relevant history;
- Events;
- previous assessments.

Review does not evaluate state in isolation when relevant context is
available.

---

## Assessment-Oriented

Review produces an Assessment.

It does not require the creation of a new domain object, action, Project,
Task, or other operational artifact.

---

## Attention Is Neutral

Attention does not imply failure or degradation.

Something may require attention because of:

- a problem;
- degradation;
- an opportunity;
- an achieved outcome;
- missing information;
- changed context;
- stale information;
- lifecycle reconsideration;
- unexpected success;
- any other state deserving deliberate consideration.

Review asks whether something matters, not merely whether something is
wrong.

---

## Assessment Basis

A Review Assessment must preserve conceptually the basis for its
evaluation.

The basis may include:

- observed state;
- expectations;
- outcomes;
- responsibilities;
- desired states;
- historical state;
- Events;
- operational results;
- available evidence.

The implementation mechanism used to represent the assessment basis is
not defined by the Workflow Model.

---

## Insufficient Basis

Review may determine that the available information is insufficient for
a responsible assessment.

Review must not infer a satisfactory state from insufficient evidence.

For example:

No evidence of backup restoration tests

does not imply:

Backups are healthy.

Insufficient basis may itself deserve attention.

---

## Evaluation Sufficiency and Attention Are Distinct

Whether sufficient information exists to evaluate a state and whether
that state deserves attention are separate dimensions.

Conceptually:

Sufficient Basis

↓

Assessment

↓

Attention may or may not be identified.

And:

Insufficient Basis

↓

The lack of evaluability may itself require attention.

Review does not require a rigid implementation taxonomy for these
dimensions.

---

## Non-Prescriptive

Review identifies what deserves attention.

It does not prescribe or execute the response.

For example:

Project requires attention

does not automatically imply:

Create Task

Execute work

Create Project

Archive Project

Review changes what is recognized as significant, not what operational
response must occur.

---

## Lifecycle Independence

Review may evaluate that a lifecycle transition appears appropriate.

For example:

Project outcome reached

↓

Review

↓

Completion may be appropriate

This does not execute:

Active → Completed

Lifecycle transitions belong to the lifecycle of the domain object.

Review does not own or automatically perform them.

---

## Optional Externalization

Producing an Assessment and externalizing that Assessment are distinct
operations.

A Review may complete without creating a persistent representation.

Externalization is optional and context-dependent.

---

## No Review Domain Object

Review is a workflow, not a domain object.

Review Assessment is the conceptual result of the workflow and is not
automatically a domain object.

A persistent representation of a Review does not require introducing a
Review object into the Domain Model.

---

## Processing Boundary

Processing determines the semantic participation of unresolved
information in the Domain Model.

Review evaluates state whose relevant meaning is already sufficiently
available for evaluation.

Review does not determine the initial domain meaning of unresolved
information.

---

## Execution Boundary

Execution performs work and evaluates what happened operationally.

Review evaluates the significance of system state in context.

Review does not perform operational work.

---

## Knowledge Boundary

Knowledge develops understanding.

Review evaluates significance.

Review may identify that something deserves further understanding, but
does not perform the reasoning or synthesis required to develop that
understanding.

Conceptually:

Review

↓

What deserves attention?

Knowledge

↓

What can be understood?

---

## Archive Boundary

Review may evaluate that continued active presence deserves
reconsideration.

It may therefore identify that archival appears appropriate.

Review does not archive the object.

Archival remains a separate workflow responsibility.

---

## State-Based Coordination

Review does not invoke Processing, Execution, Knowledge, Archive, or any
other workflow.

Review changes system state through its Assessment.

Other workflows may become applicable according to that resulting
state.

Workflows are coordinated through system state rather than direct
dependencies.

---

# Guarantees

If a Review instance completes successfully:

- relevant state within its scope has been evaluated;
- the significance of that state has been made explicit;
- attention has been identified when supported by the Assessment;
- lack of sufficient basis has not been mistaken for satisfactory state;
- the conceptual basis of the Assessment remains available;
- no operational response has been automatically prescribed;
- no operational work has been performed;
- no lifecycle transition has been automatically executed;
- no domain object has been automatically archived;
- no new domain object type has been introduced.

Successful Review completion does not guarantee that:

- attention is required;
- sufficient evidence exists;
- a problem exists;
- an identified concern has been resolved.

---

# Review Operations

Review provides four core conceptual operations:

- Observe
- Compare
- Assess
- Surface

It also provides one optional operation:

- Externalize

These operations describe Review responsibilities rather than a rigid
algorithm.

---

## Observe

Inspect state relevant to the Review scope.

Observation may include:

- current state;
- recent changes;
- Events;
- execution results;
- historical state;
- outcomes;
- responsibilities;
- available evidence.

Observe does not modify the observed objects.

---

## Compare

Contrast observed state with relevant context when comparison is
necessary for evaluation.

Comparison may use:

- intended outcomes;
- responsibilities;
- desired states;
- constraints;
- previous state;
- historical patterns;
- system invariants;
- relevant expectations.

Compare is not required when the significance of the observed state can
be assessed without an explicit comparison.

---

## Assess

Evaluate the significance of the observed state.

Assessment considers available context and determines whether:

- the basis is sufficient for responsible evaluation;
- something deserves deliberate attention;
- no attention is currently required;
- the lack of sufficient information is itself significant.

Assess produces the conceptual Review Assessment.

---

## Surface

Make the relevant result of the Assessment explicit to the actor
performing or receiving the Review.

Surface may make explicit:

- attention;
- absence of required attention;
- insufficient basis;
- relevant lifecycle reconsideration;
- other significant findings.

Surface does not require persistence.

---

## Externalize

Persist a representation of the Review Assessment.

Externalization is optional.

Possible implementations may include:

- a Review note;
- a Weekly Review note;
- an Event;
- metadata;
- a generated report;
- another persistent representation.

The specific representation mechanism belongs to implementation.

Externalization does not create a Review domain object.

---

# Project Participation

Projects may be reviewed relative to their intended outcomes, current
state, progress, constraints, and relevant history.

For example:

Project

+

Intended Outcome

+

Recent Events

↓

Review

↓

Review Assessment

Possible findings may include:

- progress remains appropriate;
- progress appears stalled;
- the outcome has been reached;
- the context has changed;
- lifecycle reconsideration may be appropriate;
- insufficient information exists for evaluation.

Review does not perform Project work and does not automatically change
Project lifecycle state.

---

# Area Participation

Areas may be reviewed relative to their ongoing responsibilities,
desired state, operational condition, and relevant history.

For example:

Area

+

Responsibility

+

Observed State

↓

Review

↓

Review Assessment

Possible findings may include:

- responsibility is being adequately maintained;
- degradation may be occurring;
- relevant information is missing;
- changed conditions deserve attention.

Review does not perform Area maintenance.

That belongs to Execution.

---

# Other Domain Participation

Review may inspect other domain objects when relevant to its scope.

Examples include:

Reference

→ relevance or continued usefulness may deserve reconsideration.

Resource

→ currency, relevance, or usefulness may deserve reconsideration.

Meeting

→ unresolved consequences may deserve attention.

Journal Entry

→ may provide relevant context for a broader Review.

Persistent Information

→ unresolved information may deserve attention.

These examples do not define rigid evaluation semantics for every
domain object.

Review remains scope- and context-dependent.

---

# Events and Review

Events provide historical evidence about changes in system state.

Conceptually:

Events

↓

What changed?

↓

Review

↓

Does that change matter?

Events remember change.

Review evaluates its significance.

Review does not need to reconstruct the complete history of the system.

Only history relevant to the current scope and context needs to be
considered.

---

# Review and Knowledge

Review and Knowledge may operate over the same information while
performing different transformations.

For example:

Several Projects repeatedly require attention.

Review may identify:

This pattern is significant.

Knowledge may subsequently investigate:

Why does this pattern occur?

Conceptually:

Review

↓

Significance

Knowledge

↓

Understanding

Review does not invoke Knowledge.

The resulting system state may simply make Knowledge applicable.

---

# Review and Lifecycle

Review may recognize states such as:

- Project outcome reached;
- Project no longer relevant;
- Area responsibility changed;
- active presence no longer justified.

These observations may make lifecycle reconsideration appropriate.

Review does not perform the lifecycle transition.

For example:

Outcome Reached

↓

Review

↓

Completion Appropriate

is distinct from:

Active → Completed

The transition belongs to the object's lifecycle.

---

# Review and Archive

Review may identify that continued active presence no longer appears
appropriate.

For example:

Reference no longer relevant

↓

Review

↓

Archival may be appropriate

or:

Completed Project

↓

Review

↓

Continued active presence may no longer be necessary

Review does not perform archival.

Archive remains responsible for removing information from active
operational context while preserving the historical value defined by
its workflow.

---

# Periodic Reviews

Review is not inherently periodic.

Periodic practices are configurations of the Review Workflow.

Examples include:

- Daily Review;
- Weekly Review;
- Monthly Review.

These are not separate workflow types.

Conceptually:

Periodic Review

=

Review Workflow

+

Scope

+

Temporal Context

A Weekly Review may therefore be represented as:

Review

scope:
relevant system state

temporal context:
since previous weekly review

The same Review Workflow may also be performed on demand.

---

# Weekly Review

Weekly Review is a common system-level use of Review.

It is not a Domain Object and not a separate workflow.

Conceptually:

Relevant System State

+

Changes Since Previous Review

+

Relevant Events

↓

Review

↓

Review Assessment

↓

optional Externalize

↓

Weekly Review Note

A Weekly Review Note is a persistent representation of a Review
Assessment.

It does not make Review itself a Domain Object.

---

# Completion

A Review instance completes when the relevant state within its scope has
been sufficiently evaluated to produce a responsible Assessment.

Completion may result in:

- attention identified;
- no attention identified;
- insufficient basis identified.

Completion does not require resolution of anything surfaced by the
Review.

The purpose of Review is evaluation, not intervention.

---

# Generated Events

Review may result in observable facts such as:

- Review Completed
- Attention Identified
- Insufficient Assessment Basis Identified
- Lifecycle Reconsideration Identified
- Archival Reconsideration Identified
- Review Assessment Externalized

Specific event definitions belong to the Event Model.

Review does not define a parallel event catalog.

---

# Next Workflows

None.

Review does not invoke or select subsequent workflows.

A Review Assessment changes system state.

That state may make Processing, Execution, Knowledge, Archive, lifecycle
operations, or another Review applicable.

Workflow applicability is determined by system state.

---

# Architectural Principles

## Review Evaluates Significance

Review determines what deserves deliberate attention.

It does not perform the response.

---

## Attention Is Not Failure

Something may deserve attention because it is problematic, successful,
uncertain, changing, completed, outdated, or otherwise significant.

---

## Evidence Must Support Evaluation

Review must not interpret insufficient evidence as satisfactory state.

Uncertainty must remain explicit when responsible assessment is not
possible.

---

## Scope Determines Relevance

Review does not require exhaustive inspection of Ohtli.

Only state relevant to the current scope needs to be evaluated.

---

## Current State and History Both Matter

Current state may be evaluated together with relevant Events and
historical context.

A snapshot alone may not reveal whether attention is required.

---

## Review Does Not Own Lifecycle

Review may determine that lifecycle reconsideration is appropriate.

Lifecycle transitions remain operations of the domain object.

---

## Review Does Not Prescribe

Review surfaces significance.

It does not determine or execute the operational response.

---

## Review Is Not a Domain Object

Review is a process.

Its Assessment is a conceptual workflow result.

Persistent Review records are representations of Review results, not
evidence that Review itself must become a domain entity.

---

## Events Remember, Review Evaluates

Events preserve observable changes.

Review determines the significance of those changes within the current
scope.

---

## State-Based Coordination

Review is autonomous.

It does not call other workflows.

Other workflows become applicable according to the resulting system
state.

---

# Summary

The Review Workflow transforms relevant system state into a Review
Assessment.

It answers:

> What requires attention?

Review operates within a defined scope and may use current state,
expectations, outcomes, responsibilities, historical context, and
Events.

Its core operations are:

Observe
Compare
Assess
Surface

and it may optionally Externalize the resulting Assessment.

Review may determine that attention is required, that no attention is
currently required, or that the available information is insufficient
for responsible evaluation.

Attention represents deliberate consideration and does not necessarily
indicate a problem.

Review does not prescribe responses, perform operational work, develop
understanding, execute lifecycle transitions, or archive objects.

Periodic practices such as Weekly Review are configurations of the same
Review Workflow using a particular scope and temporal context.

A persisted Weekly Review is a representation of a Review Assessment,
not a new Review domain object.

Review is coordinated with other workflows exclusively through system
state.
