# Execution Workflow

## Purpose

Transform actionable domain state through intentional work and evaluate
the actual operational result.

Execution connects meaningful state inside Ohtli with work performed in
reality.

It answers a single question:

> What work changes the current state toward the intended result?

Execution acts.

It does not determine the semantic meaning of captured information and
does not infer lifecycle transitions from operational outcomes.

---

# Definition

Execution is the workflow through which actionable Projects and Areas
produce operational change through work.

The workflow transforms:

Actionable Domain State

↓

Actual Operational Result

Execution is iterative.

A single execution does not need to complete a Project or permanently
satisfy an Area.

---

# Input

An actionable Project or Area.

Actionable describes a conceptual condition rather than a new domain
object or required stored status.

For a Project, actionability requires:

- The intended outcome is understood.
- Executable work can be identified.

For an Area, actionability requires:

- The ongoing responsibility is understood.
- Maintenance work can be identified.

Complete planning is not required.

Actionability requires identifiable work, not complete knowledge of all
future work.

---

# Output

An evaluated operational result produced by performing work.

Possible conceptual results include:

- Progress
- Maintenance
- Outcome Reached
- No Effective Change
- Degradation

These results describe the effect of Execution.

They are not new domain objects and are not required to exist as stored
status values.

---

# Preconditions

- A Project or Area exists.
- Its relevant meaning has already been established.
- The object is actionable.
- Work that can affect its operational state can be identified.

---

# Postconditions

When an Execution instance completes:

- Selected work has been performed.
- The actual result of that work has been evaluated.
- The operational state reflects the observed result.
- The result is represented truthfully regardless of the original
  intention.
- Relevant observable facts may be preserved through Events.

Execution does not require the object to reach a lifecycle transition.

---

# Invariants

The following rules must remain true throughout Execution.

## Domain Boundaries

Execution operates directly on:

- Project
- Area

Meeting may participate in execution through coordination, decisions, or
interaction, but it is not an execution target.

---

## Actions Are Not Domain Objects

Concrete actions may describe units of work without becoming domain
objects.

An action does not implicitly acquire:

- independent identity;
- lifecycle;
- relationships;
- persistent domain management.

Task remains deferred in the Domain Model.

If actions later require independent identity, lifecycle, relationships,
or persistent management, Task must be reconsidered explicitly in the
Domain Model rather than introduced implicitly through Execution.

---

## Reality-Based Evaluation

Execution evaluates what actually happened.

The result of work must not be replaced by the result that was intended
to happen.

Intention and result are separate concepts.

---

## Iterative Execution

Execution may occur repeatedly for the same Project or Area.

A single execution instance does not need to complete a Project or
permanently satisfy an Area.

---

## Project and Area Semantics

Project execution advances toward a finite outcome.

Area execution maintains an ongoing responsibility.

An Area is not treated as an infinite Project.

---

## Outcome and Lifecycle Separation

Recognizing that a Project outcome has been reached does not
automatically perform a lifecycle transition.

Operational outcome and object lifecycle are separate concerns.

---

## State-Based Coordination

Execution does not invoke Processing, Review, Archive, or any other
workflow.

Its applicability is determined by the current state of the system.

Workflows are coordinated through system state rather than through
direct dependencies.

---

# Guarantees

If an Execution instance completes successfully as a workflow:

- Selected work was performed.
- Its actual operational result was evaluated.
- The resulting state is represented truthfully.
- Project and Area semantics remain distinct.
- Domain boundaries are preserved.
- Actions are not implicitly promoted to domain objects.
- Operational outcomes do not automatically change lifecycle state.

Successful workflow completion does not guarantee Progress or Outcome
Reached.

A correctly executed and evaluated workflow may result in No Effective
Change or Degradation.

---

# Execution Operations

Execution consists of three conceptual operations:

- Select
- Act
- Evaluate

---

## Select

Identify executable work associated with an actionable Project or Area.

For a Project, selected work should contribute toward its intended
outcome.

For an Area, selected work should contribute toward maintaining its
ongoing responsibility.

Selection does not create a domain Action or Task object.

---

## Act

Perform the selected work.

Act is the point at which intention inside Ohtli is translated into work
that may change reality.

Ohtli distinguishes performing work from recording that work.

---

## Evaluate

Determine the actual operational result produced by the work.

Evaluation is based on observed change rather than intended success.

Evaluate may determine:

- Progress
- Maintenance
- Outcome Reached
- No Effective Change
- Degradation

Evaluation completes an Execution instance.

---

# Execution Results

## Progress

The resulting state is closer to the finite outcome of a Project.

Progress does not imply that the Project outcome has been reached.

---

## Maintenance

Work preserved or restored the desired state associated with an Area.

Maintenance is distinct from No Effective Change.

For an ongoing responsibility, preserving a desired state may be the
intended operational result.

---

## Outcome Reached

The current state satisfies the finite outcome defined by a Project.

Execution may recognize this immediately.

Outcome Reached does not automatically imply a lifecycle transition such
as:

Active → Completed

The lifecycle decision remains separate.

---

## No Effective Change

Work was performed, but no meaningful change occurred in the operational
state relevant to the Project or Area.

This describes the observed result rather than judging whether the work
was valuable.

---

## Degradation

The resulting state moved away from a Project outcome or deteriorated
the desired state of an Area.

Degradation describes actual operational change.

It is preferred over a generic Failure result because failure describes
whether an intention succeeded, while Degradation describes what
actually happened to the relevant state.

---

# Project Execution

Project execution advances a finite outcome.

Conceptually:

Project

↓

Select Work

↓

Act

↓

Evaluate

↓

Progress / No Effective Change / Degradation / Outcome Reached

A Project may participate in multiple Execution instances before its
outcome is reached.

---

# Area Execution

Area execution maintains an ongoing responsibility.

Conceptually:

Area

↓

Select Maintenance Work

↓

Act

↓

Evaluate

↓

Maintenance / No Effective Change / Degradation

Area execution does not normally produce Outcome Reached because an Area
does not represent a finite outcome.

---

# Meeting Participation

Meetings may support Execution through:

- coordination;
- decisions;
- communication;
- collaborative work.

Meeting participation does not make Meeting an execution target.

Operational progress remains associated with the relevant Project or
Area.

---

# Flow

Actionable Domain State

↓

Select

↓

Act

↓

Evaluate

↓

Actual Operational Result

Possible results:

- Progress
- Maintenance
- Outcome Reached
- No Effective Change
- Degradation

Execution may repeat as long as actionable work exists.

---

# Related Domain Objects

Execution operates directly on:

- Project
- Area

Meeting may participate without becoming an execution target.

The following objects are not execution targets:

- Journal Entry
- Reference
- Resource

Execution does not introduce Task or Action as new domain objects.

---

# Generated Events

Execution may result in observable facts such as:

- Work Performed
- Progress Observed
- Maintenance Performed
- Outcome Reached
- Degradation Observed

Specific event definitions belong to the Event Model.

Execution does not define a parallel event catalog.

---

# Next Workflows

None.

Execution does not invoke or select subsequent workflows.

Other workflows become applicable according to the resulting state of
the system.

---

# Architectural Principles

## Action Through Meaning

Execution operates on domain meaning that has already been established.

Processing determines meaning.

Execution acts upon it.

---

## Reality-Based Results

Execution records actual operational consequences rather than expected
success.

---

## Iterative Work

Projects and Areas may participate in Execution repeatedly.

Execution represents an instance of work, not the complete lifecycle of
an object.

---

## Projects Progress, Areas Persist

Projects advance toward finite outcomes.

Areas are maintained as ongoing responsibilities.

---

## Work Does Not Imply Task

Units of work may exist as operational information without becoming
persistent domain objects.

Task remains deferred until independent domain behavior provides evidence
that it is required.

---

## Outcome Is Not Lifecycle

Operational outcomes and lifecycle transitions are separate concerns.

Execution may recognize an outcome without deciding what lifecycle state
the object should enter.

---

## State-Based Coordination

Execution is autonomous.

Its applicability depends on system state rather than direct workflow
dependencies.

---

# Summary

The Execution Workflow transforms actionable domain state through
intentional work and evaluates the actual operational result.

For Projects, Execution advances toward a finite outcome.

For Areas, Execution maintains an ongoing responsibility.

Execution follows:

Select

↓

Act

↓

Evaluate

and may result in:

- Progress
- Maintenance
- Outcome Reached
- No Effective Change
- Degradation

Execution evaluates reality rather than intention.

It does not introduce Task implicitly, does not treat Areas as infinite
Projects, and does not infer lifecycle transitions from operational
outcomes.
