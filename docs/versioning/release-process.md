# Release Process

Every release should follow a consistent process.

## Development

Work is performed on feature branches and integrated into the development branch.

---

## Stabilization

Completed work is reviewed, documented, and validated before release.

---

## Release

When the milestone is complete:

* Merge `develop` into `main`.
* Create a Git tag.
* Update the changelog.
* Publish the release.

---

## Hotfixes

Critical fixes are applied to `main` and merged back into `develop`.

---

## Release Checklist

Before publishing a release:

* Documentation is complete.
* ADRs are up to date.
* CHANGELOG is updated.
* Version number is updated.
* Git tag is created.
* Milestone is closed.
