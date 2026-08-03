# Knowledge Workflow

## Purpose

Develop understanding from meaning that already exists within Ohtli.

Knowledge transforms meaningful information, domain context, experience,
and existing understanding into developed understanding.

It answers:

> What can be understood from what Ohtli already knows?

Knowledge develops understanding.

It does not determine the initial domain meaning of captured information,
perform operational work, or evaluate which parts of the system require
attention.

---

# Definition

Knowledge is the workflow through which existing meaning is explored,
connected, reasoned about, and synthesized into developed understanding.

The workflow transforms:

Meaningful Domain State

↓

Developed Understanding

Knowledge is understanding-oriented.

It does not require every instance to create or update a Resource.

Developed Understanding is not a new domain object. It describes
understanding produced through inquiry, exploration, reasoning,
comparison, experience, or synthesis.

---

# Input

Knowledge may operate on any meaningful information relevant to an
inquiry or exploration.

Domain participants may include:

- Reference
- Resource
- Journal Entry
- Meeting
- Project
- Area

Knowledge may also use meaningful information that is not itself a
domain object, including:

- execution results;
- observations;
- experience;
- previously developed understanding.

Knowledge is not restricted to external sources.

---

# Output

Developed Understanding.

Developed Understanding may:

- enrich an existing Project;
- enrich an existing Area;
- enrich an existing Resource;
- remain contextual to the current inquiry or exploration;
- be externalized as persistent information.

Knowledge does not require the creation of a Resource.

If newly externalized understanding has not yet acquired independent
domain meaning, determining whether it should become a new domain object
belongs to Processing.

---

# Triggers

Knowledge may begin through either inquiry or exploration.

## Inquiry-Driven

Knowledge may begin with an explicit question, problem, relationship, or
concept that requires understanding.

For example:

Why did this query become slower?

↓

Knowledge

↓

Developed Understanding

---

## Discovery-Driven

Knowledge may also begin through open exploration without a predefined
question.

Reading, observation, experience, discussion, or existing knowledge may
reveal a pattern or idea worth developing.

For example:

Explore References

↓

Pattern Discovered

↓

Knowledge

↓

Developed Understanding

Knowledge therefore does not require a formal inquiry before it can
begin.

---

# Preconditions

- Relevant meaning already exists within Ohtli.
- There is an intention to develop understanding through inquiry or
  exploration.
- At least some meaningful information, experience, observation, or
  existing understanding is available for cognitive work.

Complete knowledge of the subject is not required.

---

# Postconditions

When a Knowledge instance completes:

- understanding has been developed for the current inquiry or
  exploration;
- source information and derived understanding remain conceptually
  distinguishable;
- persisted derived understanding preserves epistemic provenance;
- relevant existing domain objects may have been enriched;
- the resulting understanding may remain open to future refinement.

Knowledge completion does not imply complete or absolute understanding
of a subject.

---

# Invariants

The following rules must remain true throughout Knowledge.

## Understanding-Oriented

Knowledge produces Developed Understanding.

It is not required to produce a Resource or any other new domain object.

---

## Generative Knowledge

Knowledge may develop understanding that is not explicitly present in
any individual source.

Reasoning, comparison, synthesis, generalization, and experience may
produce derived understanding.

Knowledge is therefore not limited to summarization or reorganization of
existing information.

---

## Source and Derivation Distinction

Source information and derived understanding must remain conceptually
distinct.

A conclusion derived through Knowledge must not be represented as though
it were directly asserted by one of its sources.

---

## Epistemic Provenance

When derived understanding is persisted, the basis from which that
understanding was developed must remain conceptually traceable.

Possible foundations may include:

- References;
- Resources;
- Journal Entries;
- Projects;
- Areas;
- Meetings;
- execution results;
- observations;
- experience;
- previous understanding.

The mechanism used to represent provenance belongs to implementation.

---

## Non-Absolute Understanding

Developed Understanding does not represent absolute truth.

It represents understanding developed in a particular context from the
available information, experience, and reasoning.

New evidence may refine, revise, or contradict previous understanding.

---

## Iterative Knowledge

Knowledge may occur repeatedly over the same subject, Resource, Project,
Area, or body of information.

Current Understanding

↓

New Evidence

↓

Knowledge

↓

Refined or Revised Understanding

A completed Knowledge instance does not imply that the subject is fully
understood.

---

## Domain Enrichment

Knowledge may enrich existing domain objects with developed
understanding.

In particular, it may enrich:

- Project;
- Area;
- Resource.

Enrichment does not change the fundamental identity of the object or
take ownership of transformations belonging to other workflows.

---

## Processing Boundary

Knowledge develops understanding.

Processing determines how information participates semantically in the
Domain Model.

Knowledge may enrich an existing Resource because its domain meaning is
already established.

Knowledge does not independently decide that newly externalized
understanding must acquire identity as a new Resource or other domain
object.

---

## Execution Boundary

Knowledge may develop understanding about a Project or Area but does not
perform operational work on them.

Knowledge enriches understanding.

Execution changes operational state through work.

---

## Review Boundary

Knowledge develops understanding.

It does not determine which parts of the system require attention.

Review evaluates system state and may reveal subjects that later become
appropriate for Knowledge.

---

## Optional Externalization

Developing understanding and externalizing understanding are distinct
operations.

Knowledge may complete without externalizing its result.

Externalization is optional and context-dependent.

---

## Cognitive Connections

Knowledge may discover conceptual connections that are not persistent
domain relationships.

For example:

Concept A explains Concept B

may exist as part of reasoning without introducing `explains` into the
Interaction Model.

If a connection is to become a persistent relationship between domain
objects, it must comply with the Interaction Model and the semantic
responsibilities of Processing.

Knowledge does not silently introduce new persistent relationship types.

---

## State-Based Coordination

Knowledge does not invoke Processing, Execution, Review, Archive, or any
other workflow.

Its applicability is determined by system state.

Workflows are coordinated through system state rather than through
direct dependencies.

---

# Guarantees

If a Knowledge instance completes successfully:

- understanding has been developed for its current context;
- source information and derived conclusions remain conceptually
  distinguishable;
- persisted derived understanding preserves epistemic provenance;
- existing domain meaning is respected;
- no new domain object type is introduced;
- no new persistent relationship type is introduced;
- operational state is not changed through Knowledge;
- lifecycle transitions are not inferred from developed understanding.

Successful Knowledge completion does not guarantee that the resulting
understanding is final, complete, or objectively true.

---

# Knowledge Operations

Knowledge provides four core cognitive operations:

- Explore
- Extract
- Connect
- Synthesize

It also provides one optional operation:

- Externalize

The core operations are available according to context.

They do not form a mandatory sequential pipeline.

---

## Explore

Interact deliberately with existing information, experience,
observation, or knowledge in order to develop understanding.

Exploration may include activities such as:

- reading;
- studying;
- observing;
- comparing;
- experimenting;
- discussing;
- inspecting existing knowledge.

Explore does not require a predefined question.

---

## Extract

Identify relevant elements from existing meaning.

These may include:

- concepts;
- patterns;
- arguments;
- methods;
- results;
- observations;
- relationships;
- questions.

Extraction identifies material relevant to developing understanding.

---

## Connect

Establish cognitive connections between meaningful elements.

Connections may involve:

- comparison;
- contrast;
- explanation;
- dependency;
- analogy;
- causal hypotheses;
- relationships with previous experience.

Cognitive connections do not automatically become persistent domain
relationships.

---

## Synthesize

Develop coherent understanding through reasoning over existing meaning.

Synthesis may combine:

- multiple sources;
- previous understanding;
- experience;
- observations;
- domain context.

The resulting understanding may contain conclusions that were not
explicitly present in any individual source.

---

## Externalize

Represent Developed Understanding outside immediate cognition.

Externalization is optional.

Developed Understanding may be externalized by:

- enriching a Project;
- enriching an Area;
- enriching an existing Resource;
- producing persistent information for later semantic resolution.

Externalization does not automatically create a new domain object.

---

# Knowledge Results

## Developed Understanding

Developed Understanding is the primary conceptual result of Knowledge.

It may consist of:

- an explanation;
- a pattern;
- a conclusion;
- a generalized principle;
- a refined concept;
- a comparison;
- a hypothesis;
- a lesson derived from experience.

Developed Understanding is not a domain object.

---

## Refined Understanding

Existing understanding may be extended or made more precise through new
evidence or reasoning.

---

## Revised Understanding

Existing understanding may be changed when new evidence contradicts or
weakens previous conclusions.

Knowledge therefore supports evolution rather than treating previously
developed understanding as immutable truth.

---

# Project Participation

Projects may provide context, questions, constraints, observations, and
existing understanding to Knowledge.

Knowledge may develop understanding relevant to achieving a Project
outcome.

For example:

Project Context

+

References

+

Previous Experience

↓

Knowledge

↓

Developed Understanding

↓

Project Enriched

Knowledge does not advance Project operational progress.

That belongs to Execution.

---

# Area Participation

Areas may provide ongoing context and experience for Knowledge.

Knowledge may develop understanding relevant to maintaining an Area's
responsibility.

For example:

Area Context

+

Execution Experience

+

References

↓

Knowledge

↓

Developed Understanding

↓

Area Enriched

Knowledge does not perform maintenance work.

That belongs to Execution.

---

# Resource Participation

An existing Resource may be explored, connected with new evidence,
refined, and enriched through Knowledge.

For example:

Existing Resource

+

New Reference

+

Experience

↓

Knowledge

↓

Refined Understanding

↓

Resource Enriched

Because the Resource already has established domain identity, Knowledge
may develop its content without determining its domain type again.

---

# Reference Participation

References commonly provide source information for Knowledge.

A Reference may be explored, compared, connected, and used as evidence
for derived understanding.

References are not automatically transformed into Resources.

---

# Journal Participation

Journal Entries may participate as sources of reflection, observation,
or experience.

A Journal Entry remains a Journal Entry.

Knowledge may develop generalizable understanding from one or more
Journal Entries without changing their identity or original purpose.

---

# Meeting Participation

Meetings may provide:

- discussion;
- decisions;
- observations;
- perspectives;
- questions.

Knowledge may use meaningful information arising from Meetings to
develop understanding.

Meeting remains a distinct domain object.

---

# Externalization and Processing

Knowledge and Processing remain separate even when developed
understanding is externalized.

Conceptually:

Knowledge

↓

Developed Understanding

↓

Externalized Understanding

↓

System State

If that information requires new domain identity:

Externalized Understanding

↓

Processing Applicable

↓

Domain Meaning

Knowledge does not invoke Processing.

The resulting system state simply makes Processing applicable.

---

# Provenance

Knowledge preserves epistemic provenance when derived understanding is
persisted.

Conceptually:

Reference A ──────┐
Reference B ──────┤
Experience ───────┼──→ Knowledge
Journal Entry ────┘
                       ↓
               Derived Understanding

The derived conclusion remains distinguishable from its foundations.

Provenance describes the basis of understanding.

It does not require a particular implementation mechanism.

---

# Completion

A Knowledge instance completes when sufficient understanding has been
developed for the inquiry or exploration that motivated it.

"Sufficient" is contextual.

Completion means:

The current inquiry or exploration has reached adequate understanding
for its present purpose.

It does not mean:

The subject is completely understood.

Knowledge may resume when new questions, evidence, observations, or
contexts appear.

---

# Actor Independence

Knowledge does not depend conceptually on artificial intelligence,
automation, or any particular actor.

The cognitive operations defined by Knowledge may be performed manually
or assisted by implementation capabilities.

The workflow remains the same regardless of the actor performing or
assisting the work.

The general principle of actor-independent workflows belongs to the
Workflow Model rather than to a specific implementation technology.

---

# Generated Events

Knowledge may result in observable facts such as:

- Understanding Developed
- Understanding Refined
- Understanding Revised
- Understanding Externalized
- Resource Enriched
- Project Knowledge Enriched
- Area Knowledge Enriched

Specific event definitions belong to the Event Model.

Knowledge does not define a parallel event catalog.

---

# Next Workflows

None.

Knowledge does not invoke or select subsequent workflows.

Developed or externalized understanding changes system state.

Other workflows become applicable according to that state.

---

# Architectural Principles

## Meaning Before Understanding

Processing determines what information means within Ohtli.

Knowledge develops understanding from meaning that already exists.

---

## Understanding Before Representation

Knowledge does not require understanding to become a new domain object.

Understanding and domain representation are separate concerns.

---

## Understanding May Be Generated

Knowledge may derive conclusions through reasoning, comparison,
experience, and synthesis.

It is not restricted to reproducing source information.

---

## Preserve Epistemic Provenance

Persisted derived understanding remains conceptually traceable to the
information, experience, and reasoning from which it was developed.

---

## Understanding Evolves

Knowledge represents current understanding rather than immutable truth.

New evidence may refine or revise previous understanding.

---

## Cognitive and Domain Relationships Are Distinct

Knowledge may discover arbitrary cognitive connections.

Persistent relationships between domain objects remain constrained by
the Interaction Model.

---

## Knowledge Does Not Require AI

Knowledge describes a transformation, not the actor performing it.

Artificial intelligence may assist Knowledge in future implementations,
but it is not required by the conceptual model.

---

## State-Based Coordination

Knowledge is autonomous.

It does not call other workflows.

Its applicability depends on system state.

---

# Summary

The Knowledge Workflow transforms existing meaning into Developed
Understanding.

Knowledge may begin through inquiry or open exploration.

It uses the cognitive operations:

Explore
Extract
Connect
Synthesize

and may optionally Externalize the resulting understanding.

Knowledge may use and enrich References, Resources, Journal Entries,
Meetings, Projects, and Areas while preserving their domain identities
and workflow responsibilities.

Knowledge may generate conclusions that are not explicitly present in
individual sources, but persisted derived understanding preserves
epistemic provenance and remains distinguishable from source
information.

Developed Understanding is contextual, iterative, and revisable.

Knowledge does not require creating a Resource, does not perform
operational work, does not determine what requires attention, and does
not depend on artificial intelligence.

If newly externalized understanding requires independent domain
identity, determining that meaning belongs to Processing.
