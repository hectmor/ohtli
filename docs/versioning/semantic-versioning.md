# Semantic Versioning

Ohtli follows Semantic Versioning.

Version numbers use the format:

```text
MAJOR.MINOR.PATCH
```

## MAJOR

Increment the major version when introducing incompatible changes to the framework specification.

Examples:

* Removing a core entity.
* Changing the metadata model.
* Breaking existing implementations.

---

## MINOR

Increment the minor version when introducing new capabilities in a backward-compatible manner.

Examples:

* Adding a new template.
* Introducing a new view type.
* Expanding automation capabilities.

---

## PATCH

Increment the patch version for backward-compatible corrections.

Examples:

* Documentation improvements.
* Typographical corrections.
* Clarifications.
* Non-breaking refinements.

## Pre-release Versions

Pre-release identifiers may be used during active development.

Examples:

```text
v1.0.0-alpha
v1.0.0-beta
v1.0.0-rc1
```

## Principles

* Every release is immutable.
* Every release is tagged in Git.
* Version numbers communicate compatibility.
