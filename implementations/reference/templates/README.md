# Reference Templates

This directory contains the canonical templates of the Ohtli framework.

These templates implement the concepts defined in the Core Specification and are intended to be reused by all future implementations.

## Design Principles

* Tool-independent
* Markdown-first
* Minimal by default
* Human-readable
* Consistent structure
* Reusable across implementations

## Metadata

All templates use YAML Front Matter.

Each template includes:

* Core Properties
* Entity-specific Properties when applicable

The metadata structure follows the Metadata Specification.

## Content

Templates define structure only.

They do not include:

* Example projects
* Sample data
* Tool-specific syntax
* Automation
* Plugins

## Implementations

Future implementations should reuse these templates whenever possible instead of creating alternative versions.
