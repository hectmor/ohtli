# Implementations

This directory contains the official implementations of the Ohtli framework.

The project is organized into two categories of implementations:

* **Reference Implementation** — the canonical implementation of the Ohtli Specification, independent of any software platform.
* **Platform Implementations** — implementations that adapt the Ohtli framework to specific applications while preserving the concepts and behavior defined by the specification.

## Structure

```text
implementations/
├── reference/
└── platforms/
```

## Reference Implementation

The Reference Implementation defines the canonical workspace structure and serves as the baseline for every platform implementation.

It is platform-independent and should not contain configuration or features specific to any application.

## Platform Implementations

Platform implementations provide an official adaptation of Ohtli for a specific platform.

A platform implementation may include:

* Reference Vault or workspace
* Platform configuration
* Templates
* Plugins or extensions
* Themes
* Documentation
* Examples

Each implementation must remain compatible with the Ohtli Specification and the Reference Implementation.

## Current Platforms

* Obsidian
