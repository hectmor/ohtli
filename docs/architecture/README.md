# Architecture

Ohtli is a personal operating framework designed to transform information into consistent execution.

The architecture is intentionally layered. Each layer has a single responsibility and depends only on the layers below it. This separation keeps the framework understandable, maintainable, and independent of any specific tool.

## Architecture Layers

1. Filesystem
2. Metadata
3. Domain Model
4. Workflows
5. Views
6. Automation

Each layer is documented independently.

## Documents

* `layers.md` — Defines the architectural layers and their responsibilities.
* `principles.md` — Defines the architectural principles that guide all design decisions.

## Goals

The architecture aims to:

* Keep information organized.
* Separate concerns.
* Minimize technical debt.
* Support long-term evolution.
* Remain tool-independent.
