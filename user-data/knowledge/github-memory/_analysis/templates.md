# Multi-Level Analysis Templates

These templates guide the creation of feature documentation at each abstraction level.

---

## Level 1: Specification Template

```markdown
# Feature: [Name]

## Definition
What is this feature?

## Purpose
Why does this feature exist?

## Core Requirements
- [ ] Requirement 1
- [ ] Requirement 2
- [ ] Requirement 3

## Inputs
What data/parameters does it accept?

## Outputs
What does it produce?

## Behavior
Step-by-step description of what happens.

## Edge Cases
- Case 1
- Case 2

## Related Features
- [[feature-name]] - brief relationship
```

---

## Level 2: Interaction Template

```markdown
# Feature: [Name] - Interaction Design

## User Interface

### API Interface
```
METHOD /endpoint
```

### Request Parameters
| Param | Type | Required | Description |
|-------|------|----------|-------------|
| name | string | Yes | Description |

### Response Format
```json
{
  "field": "value"
}
```

## Error Handling
| Code | Meaning | Response |
|------|---------|----------|
| 400 | Bad Request | `{"error": "..."}` |
| 429 | Rate Limited | `{"error": "rate_limit", "retry_after": 3600}` |

## Client Usage Examples

### Python
```python
result = client.feature(params)
```

### JavaScript
```javascript
const result = await client.feature(params);
```

### Go
```go
result, err := client.Feature(params)
```

## SDK Support
| Language | Package | Example |
|----------|---------|---------|
| Python | `package-name` | `pip install package` |
| JavaScript | `package-name` | `npm install package` |
| Go | `github.com/org/package` | `go get github.com/org/package` |
```

---

## Level 3: Design Template

```markdown
# Feature: [Name] - Technical Design

## Architecture

### High-Level Diagram
```
[Component A] → [Component B] → [Component C]
```

### Data Flow
1. Step 1
2. Step 2
3. Step 3

## Algorithm Details

### Algorithm Name
```
Pseudocode or math formula
```

### Complexity
- Time: O(...)
- Space: O(...)

## Data Structures

### Struct/Class Name
```python
class ClassName:
    def __init__(self):
        self.field1 = None
        self.field2 = None
```

## Configuration

```yaml
feature:
  enabled: true
  param1: value1
  param2: value2
```

## Dependencies
| Dependency | Version | Purpose |
|------------|---------|---------|
| library-a | ^1.0 | description |

## Security Considerations
- Consideration 1
- Consideration 2

## Performance Notes
- Note 1
- Note 2
```

---

## Level 4: Code Template

```markdown
# Feature: [Name] - Reference Implementation

## Repository
`owner/repo` - [description]

## File Location
`src/feature/implementation.py`

## Key Functions

### Function: `main_function()`
```python
def main_function(param1: str, param2: int) -> dict:
    """
    Brief description.

    Args:
        param1: Description
        param2: Description

    Returns:
        dict: Result object

    Raises:
        ValueError: When invalid input
    """
    pass
```

### Function: `helper_function()`
```python
def helper_function(data: list) -> generator:
    """Yield processed items."""
    for item in data:
        yield process(item)
```

## Usage
```python
from src.feature import main_function

result = main_function("input", 42)
print(result)
```

## Tests
`tests/test_feature.py`:
```python
def test_main_function():
    result = main_function("input", 42)
    assert result["status"] == "ok"
```

## Alternatives
| Repo | Language | Difference |
|------|----------|------------|
| alt/repo | Go | More performant |
```

---

## Feature Page Assembly

When documenting a feature, combine all levels:

```markdown
# [Feature Name]

## Overview
Brief description of what this feature does.

## Quick Links
- [Specification](#specification)
- [Interaction](#interaction)
- [Design](#design)
- [Code](#code)

---

## Specification
[Copy Level 1 template content]

---

## Interaction
[Copy Level 2 template content]

---

## Design
[Copy Level 3 template content]

---

## Code
[Copy Level 4 template content]

---

## Implementations in Tracked Repos

| Repo | Language | Level | Notes |
|------|----------|-------|-------|
| owner/repo | Python | Full | Production ready |
| alt/repo | Go | Partial | Performance focused |

## Related Features
- [[related-feature-1]]
- [[related-feature-2]]
```
