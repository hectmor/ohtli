---
id: 4dc73db8-9e5e-4342-9331-9ca6c3fb7759
note_type: project
created: '2026-08-30'
updated: '2026-08-30'
tags: []
aliases: []
status: planned
---

# Migrate CI To Self Hosted Runners

## Objective

## Scope

## Deliverables

## Tasks

## Notes

### Objective
Cut CI minutes cost and get faster feedback on PRs.

### Tasks
- Provision two runners
- Move the test matrix over

Snippet from the current workflow:

```yaml
# runs-on: ubuntu-latest  <- this stays a comment
runs-on: self-hosted
```

## References
