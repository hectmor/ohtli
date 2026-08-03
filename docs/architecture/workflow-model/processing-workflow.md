# Processing Workflow

## Purpose

Determine how persistent information participates meaningfully in the
Ohtli domain.

Processing interprets information that has already been captured and
resolves its meaning within the system.

It answers a single question:

> What does this information mean in Ohtli?

Processing introduces meaning.

It does not capture information, execute work, or perform lifecycle
transitions owned by other workflows.

---

# Definition

Processing is the workflow that interprets persistent information and
determines how that information participates in the domain.

The workflow transforms:

Persistent Information

↓

Meaningful Domain State

Processing follows a meaning-first approach.

Information does not require an intermediate classification before its
meaning can be determined.

---

# Input

Persistent information that already belongs to Ohtli.

The information may originate from any source accepted by the Capture
Workflow.

Processing does not require the information to be classified as an idea,
observation, knowledge, commitment, reflection, or any other intermediate
category.

---

# Output

A meaningful domain state in which the semantic role of the information
has been resolved.

Processing may produce zero or more domain operations:

- Create
- Update
- Relate

The workflow always concludes with semantic resolution.

A meaningful domain state is not a new domain object. It describes a
state in which the information has a defined meaning within Ohtli.

---

# Preconditions

- The information has been captured.
- The information is persistent.
- The information requires semantic interpretation.

---

# Postconditions

When Processing completes:

- The meaning of the information within Ohtli has been determined.
- Necessary domain operations have been performed.
- The information no longer requires semantic interpretation.
- Provenance between the original information and its semantic result is
  preserved.

---

# Invariants

The following rules must remain true throughout Processing.

## Meaning First

Processing determines meaning directly.

No intermediate classification is required.

---

## Domain Constrained

Processing may create only objects already defined by the Domain Model.

Valid domain objects are:

- Project
- Area
- Meeting
- Reference
- Resource
- Journal Entry

Processing never introduces new domain object types.

---

## Interaction Constrained

Processing may establish only relationships already defined by the
Interaction Model.

Valid relationship types are:

- belongs to
- contains
- references
- supports

Processing consumes the Interaction Model but never redefines it.

---

## Identity Preservation

Updating an existing object never changes its identity.

---

## Provenance Preservation

Processing never conceptually destroys the origin of information.

The relationship between captured information and the meaning derived
from it must remain traceable when relevant.

The implementation mechanism used to preserve provenance is outside the
scope of this workflow.

---

## Lifecycle Separation

Processing may modify semantic content but does not execute lifecycle
transitions owned by other workflows.

Lifecycle behavior remains the responsibility of the workflow that owns
that transition.

---

# Guarantees

If Processing completes successfully:

- Information has a resolved meaning within Ohtli.
- Domain integrity is preserved.
- Existing object identities are preserved.
- Only valid domain objects are created.
- Only valid semantic relationships are established.
- Provenance is not conceptually lost.
- Processing does not assume responsibility for subsequent workflows.

---

# Semantic Operations

Processing has three semantic operations.

They are optional and may be combined during a single semantic
resolution.

## Create

Materialize meaning as a new domain object.

Create may only produce objects already defined by the Domain Model.

Example:

Persistent Information

↓

Interpret

↓

Finite outcome identified

↓

Create Project

---

## Update

Incorporate new semantic information into an existing domain object.

The object's identity remains unchanged.

Example:

Persistent Information

+

Existing Project

↓

Update

↓

Same Project with additional information

---

## Relate

Establish a semantic relationship between existing domain objects.

The relationship must already exist in the Interaction Model.

Example:

Reference

↓

supports

↓

Project

---

# Semantic Resolution

Resolve is the termination condition of Processing.

It is not a semantic operation equivalent to Create, Update, or Relate.

Processing is resolved when the meaning of the information within Ohtli
has been determined and no further semantic interpretation is required.

A resolution may involve multiple operations:

Interpret

↓

Create Reference

+

Update Project

+

Relate Reference to Project

↓

Resolve

A resolution may also require no domain operation:

Interpret

↓

No domain change required

↓

Resolve

---

# Flow

Persistent Information

↓

Interpret

↓

Determine Meaning

↓

Create / Update / Relate

↓

Resolve

↓

Meaningful Domain State

Create, Update, and Relate are optional and may occur together.

Resolve always marks the completion of semantic interpretation.

---

# Provenance

Processing preserves conceptual traceability between captured information
and its semantic result.

Conceptually:

Captured Information

↓

Processing

↓

Semantic Resolution

↓

Domain Result

The origin of meaning must not be lost during this transformation.

How provenance is represented or stored belongs to implementation and is
not defined by this workflow.

---

# Related Domain Objects

Processing may operate on any object currently defined by the Domain
Model:

- Project
- Area
- Meeting
- Reference
- Resource
- Journal Entry

Processing does not define new domain objects.

---

# Generated Events

Processing may result in observable facts such as:

- Object Created
- Object Updated
- Relationship Established
- Information Resolved

Specific event definitions belong to the Event Model.

Processing does not redefine the Event Model.

---

# Next Workflows

None.

Processing does not invoke or select subsequent workflows.

Other workflows become applicable according to the resulting state of
the system.

---

# Architectural Principles

## Meaning Before Classification

Information acquires domain meaning directly without requiring an
intermediate taxonomy.

---

## Complete Semantic Resolution

A single Processing execution may perform multiple semantic operations
when necessary to completely resolve the meaning of captured information.

---

## Model Compliance

Processing operates within the boundaries established by the Domain
Model and Interaction Model.

It consumes these models but never modifies their definitions.

---

## Preserve Provenance

The origin of semantic meaning must remain conceptually traceable.

---

## Separation of Meaning and Lifecycle

Processing determines meaning.

Other workflows control lifecycle transformations that fall within their
responsibilities.

---

## State-Based Coordination

Processing does not depend directly on Capture or any subsequent
workflow.

Its applicability is determined by system state.

Workflows are coordinated through system state rather than through
direct dependencies.

---

# Summary

The Processing Workflow transforms persistent information into meaningful
domain state.

Capture answers:

> Has the information been preserved?

Processing answers:

> What does this information mean in Ohtli?

Processing resolves that meaning through optional Create, Update, and
Relate operations while preserving domain integrity, object identity,
and provenance.

Once semantic interpretation is complete, the information is resolved.
