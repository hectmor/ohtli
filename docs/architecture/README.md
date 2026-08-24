# Architecture

Ohtli is a personal operating framework designed to transform information into consistent execution.

The architecture is intentionally layered. Each layer has a single responsibility and depends only on the layers below it. This separation keeps the framework understandable, maintainable, and independent of any specific tool.

## Architecture Layers

1. Filesystem
2. Metadata
3. Domain Architecture
4. State and Transformation
5. Views
6. Automation

Each layer is documented independently in `layers.md`.

## Documents

* `layers.md` — Defines the architectural layers and their responsibilities.
* `principles.md` — Defines the architectural principles that guide all design decisions.

### Canonical Models

* `filesystem-model/` — Layer 1: the filesystem as a physical representation medium.
* `metadata-model/` — Layer 2: structured descriptive information about a representation.
* `domain-model/` — Layer 3: what exists in Ohtli.
* `interaction-model/` — Layer 3: semantic relationships between Domain Objects.
* `event-model/` — Layer 4: historical evidence of observable change.
* `workflow-model/` — Layer 4: possible transformations of relevant state.
* `representation-model/` — Layer 4: canonical semantics represented independent of technology.
* `execution-model/` — Layer 4: what it means for a Workflow to happen.
* `user-experience/` — Layer 5: how represented concepts become understandable and interactable.
* `automation-model/` — Layer 6: how and when a Workflow Execution may be initiated automatically.

## Goals

The architecture aims to:

* Keep information organized.
* Separate concerns.
* Minimize technical debt.
* Support long-term evolution.
* Remain tool-independent.
