---
name: github-deep-search
description: Unified deep search across GitHub project knowledge. Combines research, memory, tracking, comparison, and feature translation into a single search interface. Search by functionality, intent, or keyword across all tracked repositories with multi-level analysis.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [GitHub, Deep Search, Knowledge Base, Feature Search]
    capabilities:
      - functional_search
      - intent_matching
      - feature_analysis
      - multi_level_output
      - recommendation
    integrates:
      - github-research-assistant
      - github-memory-base
      - github-tracker
      - github-project-compare
      - github-feature-translate
---

# GitHub Deep Search

You are the unified GitHub project knowledge engine. You search, analyze, and recommend across all tracked repositories.

## Memory Structure

```
~/.hermes/github-memory/
├── _index.yaml              # Master index
├── _features/              # Cross-repo feature index
│   ├── _index.md
│   ├── _intent.yaml        # Intent patterns
│   ├── authentication/
│   │   ├── _feature.yaml
│   │   ├── spec.md
│   │   ├── interaction.md
│   │   ├── design.md
│   │   └── code/           # Reference implementations
│   ├── rate-limiting/
│   ├── cli/
│   └── ...
├── _analysis/              # Analysis templates
│   ├── spec-template.md
│   ├── interaction-template.md
│   ├── design-template.md
│   └── code-template.md
├── [topic]/                # Tracked repos by topic
│   └── [owner]/[repo]/
└── _reports/              # Generated reports
```

## Quick Start

### Search by Intent

```bash
# User: "I need rate limiting for my API"
# 1. Match intent → rate-limiting
# 2. Search _features/rate-limiting/
# 3. Search tracked repos for implementations
# 4. Return recommendations
```

### Search by Keyword

```bash
# Search all levels
grep -ri "rate limit" ~/.hermes/github-memory/_features/*/
grep -ri "rate limit" ~/.hermes/github-memory/*/*/*/metadata.json
grep -ri "rate limit" ~/.hermes/github-memory/*/*/*/readme.md
```

## Search Workflow

### Step 1: Parse Intent

```bash
# Read intent patterns
cat ~/.hermes/github-memory/_intent/_intents.yaml

# Match user's query against patterns
# Extract: action verb + object + context
```

### Step 2: Feature Search

```bash
# Find matching features
find ~/.hermes/github-memory/_features -name "spec.md" -exec grep -l -i "keyword" {} \;

# Get feature definitions
cat ~/.hermes/github-memory/_features/[feature]/_feature.yaml
```

### Step 3: Repo Search

```bash
# Search tracked repos
for repo in ~/.hermes/github-memory/*/*/*/metadata.json; do
  owner=$(jq -r '.owner' "$repo")
  name=$(jq -r '.name' "$repo")
  desc=$(jq -r '.description' "$repo" 2>/dev/null)
  if echo "$desc" | grep -qi "keyword"; then
    echo "$owner/$name"
  fi
done

# Search with gh
gh search repos "keyword" --lang=go --stars=>100 --limit=20
```

### Step 4: Multi-Level Analysis

```bash
# For each matched feature/repo, generate analysis at all levels:

# Level 1: Specification
cat ~/.hermes/github-memory/_features/[feature]/spec.md

# Level 2: Interaction
cat ~/.hermes/github-memory/_features/[feature]/interaction.md

# Level 3: Design
cat ~/.hermes/github-memory/_features/[feature]/design.md

# Level 4: Code
ls ~/.hermes/github-memory/_features/[feature]/code/
```

## Multi-Level Output

For each search result, provide analysis at these levels:

### Level 1: Specification (规范/定义)
What should this feature do?

```markdown
## Feature: API Rate Limiting
### Purpose
Control API request volume per client.

### Requirements
- Limit by: API key, IP, user ID
- Algorithms: Token bucket, sliding window, fixed window
- Error: 429 Too Many Requests
- Headers: X-RateLimit-*

### Behavior
1. Client sends request
2. Check rate limit
3. Allow or reject
4. Return headers
```

### Level 2: Interaction (交互)
How does the user/program interact?

```markdown
## API Interface
### HTTP Headers
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1640995200
Retry-After: 3600

### Error Response (429)
{
  "error": "rate_limit_exceeded",
  "retry_after": 3600
}

### Client Usage
client.call() → if 429 → sleep(retry_after) → retry
```

### Level 3: Design (设计)
How is it structured?

```markdown
## Architecture
### Token Bucket Algorithm
Capacity: 100 tokens, Refill: 10/sec

### Components
Client → RateLimiter → Redis → API

### Configuration
{ "limit": 100, "window": 60, "algorithm": "token_bucket" }
```

### Level 4: Code (代码)
How is it implemented?

```python
class TokenBucket:
    def allow_request(self, client_id):
        bucket = self.buckets[client_id]
        self._refill(bucket)
        if bucket["tokens"] >= 1:
            bucket["tokens"] -= 1
            return True
        return False
```

## Search Examples

### "How to handle authentication?"

```bash
# 1. Match intent
# → authentication patterns

# 2. Find features
cat ~/.hermes/github-memory/_intent/_intents.yaml | grep -A 10 "authentication:"

# 3. Get specification
cat ~/.hermes/github-memory/_features/authentication/spec.md

# 4. Get implementations from tracked repos
grep -r "oauth\|jwt\|session" ~/.hermes/github-memory/*/*/*/metadata.json

# 5. Return multi-level analysis
```

### "Build a CLI tool with arguments"

```bash
# 1. Match intent → cli + argument-parser

# 2. Find CLI features
find ~/.hermes/github-memory/_features/cli -name "*.md"

# 3. Search tracked repos
grep -r "cli\|commander\|cobra" ~/.hermes/github-memory/*/*/*/metadata.json

# 4. Get implementations
ls ~/.hermes/github-memory/_features/cli/code/
```

### "Compare two similar projects"

```bash
# Use github-project-compare workflow
# From: github-research-assistant → github-project-compare
```

## Intent Matching Quick Reference

| User Says | Intent | Features |
|-----------|--------|----------|
| "authenticate" | authentication | jwt, oauth, session |
| "make API calls" | api-client | http-client, rest-client |
| "rate limit" | rate-limiting | token-bucket, redis-limiter |
| "CLI tool" | cli | cli-framework, argument-parser |
| "parse arguments" | argument-parser | argparse, commander |
| "cache data" | caching | redis-cache, memory-cache |
| "handle events" | messaging | event-bus, pub-sub |
| "search" | search | full-text-search, elasticsearch |

## Add New Feature to Index

```bash
# 1. Create directory
mkdir -p ~/.hermes/github-memory/_features/[feature-name]/code

# 2. Create feature definition
cat > ~/.hermes/github-memory/_features/[feature-name]/_feature.yaml << 'EOF'
name: feature-name
display_name: Human Name
category: category
tags: [tag1, tag2]
status: defined
repos: []
EOF

# 3. Create multi-level docs
touch ~/.hermes/github-memory/_features/[feature-name]/spec.md
touch ~/.hermes/github-memory/_features/[feature-name]/interaction.md
touch ~/.hermes/github-memory/_features/[feature-name]/design.md

# 4. Add to intent mapping
# Edit _intent/_intents.yaml
```

## Reports

### Generate Search Report

```bash
# Create comprehensive report
cat > ~/.hermes/github-memory/_reports/search-$(date +%Y%m%d).md << 'EOF'
# GitHub Deep Search Report

## Query: [user query]
## Date: YYYY-MM-DD

## Intent Matched
- Intent: [matched intent]
- Confidence: [score]

## Features Found
| Feature | Category | Status |
|---------|----------|--------|
| name | category | defined |

## Repositories with Implementation
| Repo | Stars | Implementation |
|------|-------|---------------|
| owner/repo | X | [how they do it] |

## Recommendations
[Recommended implementation approach]
EOF
```

## Integration with Other Skills

- **github-research-assistant** → Initial project analysis
- **github-memory-base** → Store findings in memory
- **github-tracker** → Track metrics over time
- **github-project-compare** → Compare implementations
- **github-feature-translate** → Translate between languages

## Important Notes

- Always search features index before gh search
- Cross-reference with tracked repo implementations
- Provide all 4 levels when available
- Update feature index when discovering new patterns
- Use intent matching for natural language queries
