# Archive Workflow

## Purpose

Remove preserved information or domain objects from normal operational
context while retaining their historical value.

Archive changes contextual presence without destroying identity,
meaning, history, or required relationships.

It answers:

> What should remain preserved but no longer operationally present?

Archive changes contextual presence while preserving history.

Archive is reversible through Reactivate.

---

# Definition

Archive is the workflow through which persistently represented
information moves from operational presence to historical presence
without being destroyed.

The primary transformation is:

Operationally Present Preserved State

↓

Archive

↓

Historically Present Preserved State

The inverse transformation is:

Historically Present Preserved State

↓

Reactivate

↓

Operationally Present Preserved State

Archive transforms contextual presence.

It does not transform domain identity or meaning.

Archived information remains preserved and retrievable when explicitly
relevant.

---

# Input

Archive may operate on persistently represented information.

Possible targets include:

- Persistent Information;
- Project;
- Area;
- Reference;
- Resource;
- Meeting;
- Journal Entry;
- other persistently represented domain information.

A target does not need to be a Domain Object if it is already
persistently represented.

Archive does not require information to pass through Processing before
archival when sufficient state or explicit intent already justifies
removal from operational context.

---

# Output

The primary result of Archive is:

Historically Present Preserved State.

The target:

- remains persistently represented;
- retains its identity;
- retains its existing meaning;
- retains relevant history;
- retains required relationships;
- retains required epistemic provenance;
- remains historically retrievable;
- no longer participates normally in operational context.

Archive does not create an archived version of the object.

For example:

Project A

does not become:

Archived Project A'

The same Project A continues to exist with historical rather than
operational contextual presence.

---

# Contextual Presence

Archive introduces a conceptual distinction between:

- operational presence;
- historical presence.

Operational presence means that information normally participates in
current operational context.

Historical presence means that information remains preserved but is
excluded from normal operational participation.

Archived information may therefore be excluded by default from:

- active planning;
- routine Execution selection;
- normal operational Review scopes;
- active dashboards;
- current operational navigation.

It remains available for:

- explicit retrieval;
- historical Review;
- Knowledge;
- provenance inspection;
- historical analysis;
- reactivation.

The exact implementation of contextual presence is not defined by the
Workflow Model.

It may eventually be represented through metadata, filesystem
organization, database state, queries, views, or another mechanism.

---

# Applicability

Archive becomes applicable when:

- the target is persistently represented;
- the target currently participates in operational context;
- continued operational presence is no longer desired or justified;
- preservation remains intended;
- sufficient system state or explicit intent justifies the transition;
- removing operational presence does not violate required operational
  integrity.

Archive does not require a preceding Review.

Applicability may arise from:

- current domain state;
- a Review Assessment;
- explicit intent;
- policy;
- automation;
- another relevant system condition.

Workflows remain coordinated through system state rather than mandatory
workflow sequences.

---

# Archive Preconditions

Before Archive can complete validly:

1. The target is persistently represented.
2. The target currently participates in operational context.
3. Sufficient system state or explicit intent justifies removing
   operational presence.
4. Preservation remains intended.
5. Removing the target from operational context does not violate
   required operational integrity.

Archive does not universally require that:

- a Review has occurred;
- a Project is Completed;
- an object is old;
- an object is unused;
- an object is obsolete.

Age and inactivity alone do not establish archival eligibility.

---

# Archive Postconditions

When Archive completes successfully:

- the target remains preserved;
- the target retains the same identity;
- existing domain meaning remains unchanged;
- relevant history remains available;
- required historical, semantic, and epistemic relationships remain
  intact;
- epistemic provenance remains intact;
- sufficient transition context remains available;
- normal operational participation is removed;
- historical retrieval remains possible;
- Reactivate remains possible;
- related objects remain unchanged unless independently archived.

Archive does not imply deletion.

---

# Reactivate

Reactivate is the inverse contextual operation of Archive.

It transforms:

Historically Present Preserved State

↓

Reactivate

↓

Operationally Present Preserved State

Reactivate restores operational presence to the same persistently
represented target.

It does not recreate the object.

---

# Reactivate Preconditions

Before Reactivate can complete validly:

1. The target remains persistently represented.
2. The target currently participates in historical context.
3. Sufficient system state or explicit intent justifies restoring
   operational presence.
4. Restoring operational presence does not violate current domain or
   operational invariants.

Reactivate does not require semantic reinterpretation before it can
occur unless the current system state independently requires such work.

---

# Reactivate Postconditions

When Reactivate completes successfully:

- the same target remains represented;
- operational presence is restored;
- identity remains unchanged;
- existing meaning remains unchanged;
- lifecycle state remains unchanged;
- relevant history remains preserved;
- required relationships remain preserved;
- previous Archive and Reactivate transitions remain part of history;
- sufficient transition context remains available.

Reactivate restores contextual presence only.

It does not automatically validate, update, reopen, or reinterpret the
target.

---

# Invariants

The following rules must remain true throughout Archive and Reactivate.

## Preservation

Archive preserves rather than destroys.

Archive is not Delete.

The target continues to exist after archival.

---

## Identity Preservation

Archive and Reactivate preserve target identity.

Conceptually:

Object X before Archive

=

Object X after Archive

=

Object X after Reactivate

Archival does not create parallel object types such as:

- ArchivedProject;
- ArchivedResource;
- ArchivedReference.

---

## Meaning Preservation

Archive does not reinterpret domain meaning.

A Resource remains a Resource.

A Project remains a Project.

A Reference remains a Reference.

If domain meaning needs to change, that responsibility belongs to
Processing rather than Archive.

---

## Contextual Presence Transformation

Archive changes contextual presence.

It transforms operational presence into historical presence.

Reactivate restores operational presence.

Contextual presence is distinct from identity, meaning, and lifecycle.

---

## Lifecycle Independence

Contextual presence and domain lifecycle state are independent
dimensions.

For example:

Project

Lifecycle:
Completed

Context:
Operational

may become:

Project

Lifecycle:
Completed

Context:
Historical

without changing the Project lifecycle.

Reactivate does not imply:

Completed → Active

If a lifecycle transition is required, it occurs independently according
to the lifecycle of the Domain Object.

---

## Historical Continuity

Archive preserves relevant historical continuity.

Facts and Events that occurred before archival remain part of the
target's history.

Archival does not reset or replace historical state.

---

## Historically Cumulative Transitions

Archive and Reactivate are historically cumulative transitions.

For example:

Operational

↓

Archive

↓

Historical

↓

Reactivate

↓

Operational

↓

Archive

↓

Historical

The current contextual presence is Historical.

The previous Archive and Reactivate transitions remain historical facts.

A new contextual transition does not erase earlier transitions.

---

## Relationship Integrity

Archive preserves relationships required for historical, semantic, and
epistemic integrity.

A relationship may remain historically valid even when it is no longer
shown or used in normal operational context.

Relationship existence and operational visibility are separate
concerns.

---

## Epistemic Integrity

Archive must not invalidate provenance required to interpret persisted
understanding.

For example, an archived Reference may continue to serve as evidence for
Developed Understanding.

Archival changes contextual presence, not the historical or epistemic
basis of existing understanding.

---

## Historical Accessibility

Archived information remains retrievable when explicitly relevant.

Historical presence does not mean inaccessible presence.

Archived information may still participate in:

- Knowledge;
- historical Review;
- explicit retrieval;
- provenance inspection;
- historical analysis;
- Reactivate.

---

## Reversibility

Archive is reversible through Reactivate.

Reactivate restores operational presence without creating a new target.

Reversibility does not erase the historical fact that archival occurred.

---

## Reactivation Neutrality

Reactivate restores operational presence only.

It does not automatically imply:

- semantic reinterpretation;
- content validation;
- current validity;
- current relevance;
- lifecycle transition;
- Project reopening;
- relationship updates;
- new identity.

Other transformations may become applicable after reactivation according
to system state.

Reactivate does not invoke them.

---

## Non-Cascading Archive

Archive is non-cascading by default.

Archiving one target does not implicitly archive related targets.

For example:

Project A → Historical

does not imply:

Resource X → Historical

Reference Y → Historical

Meeting Z → Historical

Each target has independent archival eligibility.

A higher-level implementation may coordinate multiple explicit Archive
operations, but each target remains independently evaluated.

---

## Independent Eligibility

Archival eligibility belongs to each target independently.

A relationship with an archived target does not itself establish that a
related target should also be archived.

Shared Resources, References, Meetings, Areas, or other information may
remain operationally relevant after a related object is archived.

---

## Transition Context

Archive and Reactivate preserve sufficient transition context to remain
historically interpretable.

It should remain possible to understand, when relevant:

- why operational presence was removed;
- why operational presence was later restored.

Transition context is a conceptual requirement.

The Workflow Model does not prescribe a specific `archive_reason`,
`reactivation_reason`, metadata field, Event schema, or storage
mechanism.

---

## Operational Integrity

Archive must not remove a target from operational context when its
operational presence remains required to preserve valid system behavior
or required operational relationships.

For example:

Resource A

↓

required operationally by

Area B

may prevent Resource A from being validly archived while that
operational dependency remains required.

Historical relationships alone do not prevent Archive.

The relevant distinction is between:

- relationships that only require historical preservation;
- dependencies that still require operational presence.

Archive does not resolve blocking dependencies.

The system state must change before Archive can complete validly.

---

## Reactivation Integrity

Reactivate must respect current domain and operational invariants.

Restoring operational presence must not introduce an invalid system
state.

Reactivate does not itself resolve incompatible domain conditions.

---

## Review Independence

Archive does not require a preceding Review.

Review may identify:

Archival may be appropriate.

That Assessment may contribute to the state that makes Archive
applicable.

However, Archive may also become applicable through explicit intent,
domain state, policy, automation, or another sufficient condition.

---

## State-Based Coordination

Archive does not invoke Processing, Execution, Knowledge, Review, or any
other workflow.

Reactivate also does not invoke other workflows.

Archive and Reactivate change system state.

Other workflows may become applicable according to the resulting state.

Workflows are coordinated through system state rather than direct
dependencies.

---

# Archive Operations

Archive provides two fundamental contextual operations:

- Archive;
- Reactivate.

These operations are part of the same workflow model.

A separate Reactivation Workflow is not required.

---

## Archive

Move a persistently represented target from operational presence to
historical presence while preserving its identity, meaning, history,
required relationships, and historical accessibility.

Conceptually:

Operational Context
        │
      Target
        │
        ▼
      Archive
        │
        ▼
Historical Context
        │
      Target

Archive does not delete the target.

---

## Reactivate

Restore a historically present target to operational presence while
preserving identity and historical continuity.

Conceptually:

Historical Context
        │
      Target
        │
        ▼
    Reactivate
        │
        ▼
Operational Context
        │
      Target

Reactivate does not recreate or reopen the target automatically.

---

# Project Participation

Projects are common Archive targets.

For example:

Project

Lifecycle:
Completed

Context:
Operational

↓

Archive

↓

Project

Lifecycle:
Completed

Context:
Historical

Archive does not perform:

Active → Completed

and Reactivate does not perform:

Completed → Active

Project lifecycle and contextual presence remain independent.

Cancelled Projects may also be archived.

An archived Project may later be reactivated without creating a new
Project.

---

# Area Participation

Areas represent ongoing responsibilities.

Lack of recent activity does not itself justify archival.

An Area may remain operationally relevant even when no recent work has
been required.

Archive may become appropriate when the responsibility represented by
the Area no longer requires operational presence.

For example:

Area

Responsibility no longer current

↓

Archive

↓

Historical Area presence

If the responsibility becomes operationally relevant again, the same
Area may be reactivated.

Reactivate does not independently redefine the responsibility.

---

# Resource Participation

Resources may be archived when continued operational presence is no
longer justified while historical preservation remains useful.

For example:

Resource v1

superseded by

Resource v2

↓

Archive Resource v1

The original Resource remains historically retrievable and may preserve
important relationships and provenance.

Reactivation does not imply that the Resource is current or valid again.

---

# Reference Participation

References may move to historical presence when they are no longer
needed in normal operational context.

An archived Reference remains available for:

- provenance;
- historical interpretation;
- Knowledge;
- explicit retrieval.

Archiving a Reference must not invalidate epistemic provenance required
by persisted understanding.

---

# Meeting Participation

Past Meetings may become appropriate Archive targets when they no longer
require normal operational presence.

Their historical information and relationships remain preserved.

Archiving a Project does not automatically archive its Meetings.

Each Meeting retains independent archival eligibility.

---

# Journal Participation

Journal Entries are inherently historical in character.

Age alone does not require archival.

Archive is relevant only when changing their contextual participation is
useful to the system.

The Workflow Model does not require routine archival of old Journal
Entries.

---

# Persistent Information Participation

Archive may operate on Persistent Information that has not acquired
Domain Meaning through Processing.

For example:

Unresolved Persistent Information

↓

continued operational presence no longer justified

↓

Archive

↓

Historical Persistent Information

Archive does not require semantic classification when sufficient state
or explicit intent already justifies contextual removal.

---

# Archive and Capture

Capture transforms:

Ephemeral Information

↓

Persistent Information

Archive transforms:

Operationally Present Preserved State

↓

Historically Present Preserved State

Capture determines what should be preserved.

Archive determines what should remain preserved but no longer
operationally present.

Archive never reverses Capture by destroying information.

---

# Archive and Processing

Processing determines how information participates semantically in the
Domain Model.

Archive does not reinterpret that meaning.

Conceptually:

Processing

Information → Meaning

Archive

Operational Presence → Historical Presence

If archived information later requires semantic reinterpretation,
Processing may become applicable according to system state.

Archive does not invoke it.

---

# Archive and Execution

Execution performs work and evaluates actual operational results.

Archive changes contextual participation.

Execution may produce state that makes Archive relevant, such as an
Outcome Reached.

That does not automatically cause archival.

---

# Archive and Knowledge

Knowledge develops understanding from meaningful information.

Historical information remains available to Knowledge when explicitly
relevant.

For example:

Archived Projects

+

Historical Execution Results

+

Archived References

↓

Knowledge

↓

Developed Understanding

Archive therefore reduces operational presence without eliminating
intellectual or historical usefulness.

---

# Archive and Review

Review evaluates whether relevant system state deserves attention.

Review may determine:

Continued operational presence deserves reconsideration.

or:

Archival may be appropriate.

Review does not perform Archive.

Archive does not require Review.

Conceptually:

Review

↓

Archival may be appropriate

↓

System State

↓

Archive becomes applicable

There is no direct workflow invocation.

---

# Archive and Delete

Archive is not Delete.

Archive:

- preserves the target;
- preserves identity;
- preserves meaning;
- preserves history;
- preserves required relationships;
- preserves historical accessibility;
- supports Reactivate.

Delete destroys or removes information.

Deletion policy and destructive information removal are outside the
Archive Workflow defined here.

---

# Operational Integrity

Archive must preserve valid operational behavior.

A target cannot be validly removed from operational context while its
operational presence remains required.

For example:

Resource A
    │
    │ required operationally by
    ▼
Active Area B

Archive Resource A

↓

Operational integrity would be violated

↓

Archive cannot complete

Archive does not determine how the dependency should be resolved.

Once system state changes so that operational presence is no longer
required, Archive may become applicable.

---

# Historical Relationships

Archival does not imply relationship destruction.

For example:

Archived Project A
        │
        │ informed by
        ▼
Archived Reference B

or:

Archived Project A
        │
        │ used
        ▼
Operational Resource C

may both remain historically valid.

The contextual presence of related objects is independent unless a
required operational invariant states otherwise.

---

# Transition History

Archive and Reactivate preserve cumulative transition history.

Conceptually:

Created

↓

Operational

↓

Archived

↓

Historical

↓

Reactivated

↓

Operational

↓

Archived

↓

Historical

The final state describes current contextual presence.

The Events describe how that presence changed over time.

The Workflow Model does not require explicit storage of contextual
intervals.

The Event Model may represent observable transitions such as Archive and
Reactivate.

---

# Completion

An Archive instance completes when:

- operational presence has been removed;
- historical presence has been established;
- preservation remains intact;
- required historical, semantic, epistemic, and operational integrity
  has been preserved;
- sufficient transition context remains available.

A Reactivate instance completes when:

- operational presence has been restored;
- the same target identity remains intact;
- historical continuity remains intact;
- current domain and operational invariants remain valid.

Neither operation requires subsequent workflows to execute.

---

# Generated Events

Archive and Reactivate may result in observable facts such as:

- Object Archived;
- Information Archived;
- Object Reactivated;
- Information Reactivated.

Relevant Events may preserve sufficient transition context to make the
change historically interpretable.

Specific Event definitions and schemas belong to the Event Model.

Archive does not define a parallel event catalog.

---

# Next Workflows

None.

Archive and Reactivate do not invoke or select subsequent workflows.

Their transitions modify system state.

Processing, Execution, Knowledge, Review, another Archive operation, a
lifecycle operation, or another relevant transformation may become
applicable according to the resulting state.

---

# Architectural Principles

## Archive Preserves

Archive removes operational presence without destroying preserved
information.

---

## Contextual Presence Is Independent

Operational or historical presence is distinct from:

- identity;
- meaning;
- lifecycle state.

Archive modifies contextual presence only.

---

## Archive Is Reversible

Historical presence may be returned to operational presence through
Reactivate.

The same target identity is preserved.

---

## Reactivation Is Neutral

Reactivate restores operational presence.

It does not automatically validate, update, reinterpret, or reopen the
target.

---

## History Is Cumulative

Archive and Reactivate transitions remain historical facts.

Later transitions do not erase earlier contextual history.

---

## Relationships Remain Meaningful

Relationships required for historical, semantic, and epistemic
integrity survive archival.

Operational visibility of those relationships is an implementation
concern.

---

## Archive Does Not Cascade

Each target has independent archival eligibility.

Archiving one object does not implicitly archive related objects.

---

## Operational Integrity Must Be Preserved

Archive cannot validly remove a target whose operational presence
remains required.

Reactivate likewise cannot restore operational presence in a way that
violates current system invariants.

---

## Transition Context Must Remain Interpretable

Archive and Reactivate preserve sufficient context to explain their
historical transitions.

---

## Archive Does Not Require Review

Review may identify archival relevance.

It is not a mandatory predecessor of Archive.

---

## State-Based Coordination

Archive and Reactivate are autonomous contextual transformations.

They do not call other workflows.

Workflow applicability is determined by system state.

---

# Summary

The Archive Workflow changes the contextual presence of persistently
represented information while preserving its identity, meaning, history,
required relationships, provenance, and historical accessibility.

Its primary transformation is:

Operationally Present Preserved State

↓

Archive

↓

Historically Present Preserved State

The transformation is reversible:

Historically Present Preserved State

↓

Reactivate

↓

Operationally Present Preserved State

Archive is not Delete.

Archive does not reinterpret meaning, change lifecycle state, cascade
automatically to related objects, or require a preceding Review.

Reactivate restores operational presence without automatically
validating, updating, reopening, or reinterpreting the target.

Archive and Reactivate preserve cumulative transition history and
sufficient transition context to remain historically interpretable.

Both operations must respect operational integrity.

Archive therefore allows Ohtli to reduce operational complexity without
sacrificing historical continuity.
