# View Design Principles

Views should communicate information clearly while preserving the integrity of the underlying data.

## Read-Only

Views never own or modify data.

---

## Single Source of Truth

Every view reflects information stored elsewhere.

No duplication should occur.

---

## Purpose-Driven

Each view should answer a specific question.

Avoid generic dashboards that attempt to display everything.

---

## Minimalism

Show only information relevant to the intended decision.

---

## Consistency

Views presenting similar information should follow similar layouts.

---

## Composability

Complex views should be built by combining simpler views.

---

## Technology Agnostic

A view may be implemented using any technology capable of presenting information without changing its meaning.
