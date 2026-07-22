# Obsidian Implementation

The Obsidian Implementation is the official implementation of the Ohtli framework for Obsidian.

It adapts the Ohtli Specification and the Reference Implementation to the Obsidian ecosystem while preserving the framework's core principles.

## Objectives

* Provide an official Obsidian vault.
* Support the complete Ohtli workflow.
* Remain compatible with the Reference Implementation.
* Minimize platform-specific behavior.
* Keep Markdown files portable.

## Structure

```text
reference-vault/
templates/
plugins/
settings/
snippets/
examples/
```

### Reference Vault

The `reference-vault/` directory contains the canonical Obsidian vault distributed with Ohtli.

Users may use this vault directly or create their own vault in any location and copy the required files.

### Templates

Contains Obsidian-specific document templates.

### Plugins

Contains documentation and configuration for the recommended Obsidian plugins.

### Settings

Contains shared workspace settings.

### Snippets

Contains optional CSS snippets.

### Examples

Contains examples specific to the Obsidian implementation.

## Design Principles

The Obsidian Implementation follows the same principles as the Reference Implementation.

* Tool-independent specification
* Markdown-first
* Human-readable
* Portable
* Extensible

Platform-specific features are optional enhancements and must not become requirements of the framework.
