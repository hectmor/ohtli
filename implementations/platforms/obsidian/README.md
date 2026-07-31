# Obsidian Platform

This directory contains the reference implementation of Ohtli for Obsidian.

The implementation is divided into two independent responsibilities.

- **Vault** defines the organization of information.
- **Platform** defines how Obsidian behaves.

The platform intentionally versions only shared configuration.

User preferences remain outside version control.

## Structure

```
obsidian/
├── README.md
├── configuration.md
└── vault/
```

## Principles

- Reproducible
- Portable
- Minimal
- Opinionated where collaboration benefits
- Flexible where personal workflows differ

## Related Documentation

- `configuration.md`
- `vault/README.md`
