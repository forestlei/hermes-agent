# GitHub Deep Search - Feature Index

This directory contains cross-repository feature mappings.

## Structure

```
_features/
├── _index.md              # Master feature catalog
├── _index.yaml            # Intent-to-feature mappings
├── authentication/
│   ├── _feature.yaml
│   ├── spec.md
│   ├── interaction.md
│   ├── design.md
│   └── code/
├── api-client/
├── cli/
├── data-processing/
├── rate-limiting/
├── caching/
├── authentication/
├── database/
├── monitoring/
└── ... (expand as needed)
```

## Adding New Features

```bash
# Create feature directory
mkdir -p ~/.hermes/github-memory/_features/[feature-name]

# Create feature definition
cat > ~/.hermes/github-memory/_features/[feature-name]/_feature.yaml << 'EOF'
name: feature-name
display_name: Human Readable Name
category: category
tags: [tag1, tag2]
status: defined|implemented|experimental
repos: []
EOF
```

## Feature Status

- **defined**: Specification exists, no implementation reference
- **implemented**: Has code references from tracked repos
- **experimental**: New feature, needs validation
