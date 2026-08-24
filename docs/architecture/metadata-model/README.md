# Metadata Model

## Status

Defined

## Purpose

The Metadata Model defines the conceptual role of Metadata as structured,
technology-independent descriptive information attached to a Domain
Object's representation, without redefining domain semantics, state
semantics, or introducing a second Representation Model.

```text
Domain Model: What exists?
Representation Model: How is it represented, independent of technology?
Metadata Model: What structured descriptive information may accompany that representation?
```

These responsibilities are architectural boundaries, not a storage schema.

## Scope

The model consolidates Metadata Purpose, Metadata and Domain, Metadata and
Representation, and Architectural Boundaries.

This model does not define a concrete property schema, field names, file
format (such as YAML), or storage technology. Those are implementation
decisions.

## Core Model

```text
Domain Object
    has a canonical Current Representation
        ↓
Metadata
    may describe that representation structurally
        ↓
Metadata does not become
    an independent source of domain or state semantics
```

Metadata describes a representation. It does not authorize, define, or
supersede what the Domain, Interaction, Workflow, or Representation
Models already establish.

## Canonical Distinctions

```text
Metadata != Domain Model
Metadata != Representation Model
Metadata != domain semantics
Metadata property != Domain Object identity
Metadata != Current State authority
```

## Metadata and Domain

The Domain Model remains authoritative for what entities exist and what
they mean. Metadata may describe a Domain Object's represented instance,
but a metadata property does not thereby define, redefine, or imply a
Domain Object's existence, and no Domain Object's existence depends on
any particular metadata property being present.

## Metadata and Representation

The Representation Model remains authoritative for Current Representation,
State Representation, and Representation Invariants. Metadata is one
possible structured expression of parts of a representation; it is not a
second representation contract, and it does not become Authoritative
State merely by being present. When metadata expresses Current State, it
remains subordinate to whatever the Representation Model establishes as
authoritative for that state.

```text
Metadata expressing State != Metadata as Authority for State
```

## Cross-Model Consistency

| Model | Preserved contract |
| --- | --- |
| Domain Model | Metadata creates no Domain Object and does not redefine identity, purpose, or existence. |
| Interaction Model | Metadata creates no relationship meaning, direction, or cardinality. |
| Representation Model | Current Representation, State Representation, and Representation Invariants remain authoritative; metadata does not become a second representation contract. |

## Architectural Boundaries

The Metadata Model does not define property names, field types, YAML or
any other file format, validation rules, indexing, search, storage
technology, or any implementation technology.

It is complete without a concrete metadata schema.

## Phase 8 Result (Metadata)

Phase 8 establishes that metadata is a structured, subordinate expression
of an already-canonical representation, and that no metadata property
carries independent semantic authority.

```text
Domain Model
        ↓
Representation Model
        ↓
Metadata Model
        ↓
Future Implementation
```

This expresses semantic dependency only; it is not runtime order, data
flow, or implementation architecture.
