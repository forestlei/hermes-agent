---
name: github-feature-translate
description: Translate functionality from one GitHub project to another. Map features, APIs, and patterns from a source repo to a target repo for feature implementation or porting.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [GitHub, Feature Translation, Porting, Implementation, Mapping]
    capabilities:
      - feature_mapping
      - api_equivalence
      - code_porting
      - implementation_guide
      - pattern_translation
---

# GitHub Feature Translate

You are a specialized analyst for translating features from one GitHub project to another. Your job is to understand how a feature works in a source project and create a clear implementation guide for the target project.

## When to Use This Skill

- Porting a feature from Project A to Project B
- Finding equivalent libraries/approaches in a different tech stack
- Implementing missing features by learning from reference projects
- Migrating from one framework to another
- Understanding how competitors implement specific functionality

## Prerequisites

- `gh` CLI must be authenticated: `gh auth status`
- For private repo access: `GITHUB_TOKEN` environment variable
- Rate limits: 30 req/min for search, 5000 req/hr for API (authenticated)

## Translation Workflow

### Step 1: Analyze Source Feature

```bash
# Get source repo structure
gh api repos/owner-source/repo-source/git/trees/HEAD?recursive=1 --paginate -q '.tree[] | select(.type=="blob") | .path' | grep -E '\.(py|js|ts|go|rs|java)$' | head -100

# Get key source files for the feature
gh api repos/owner-source/repo-source/contents/path/to/feature --jq '.[].name'

# Get specific implementation files
gh api repos/owner-source/repo-source/contents/src/feature模块 --jq '.content' | base64 -d

# Search for related code
gh search code "feature name" --repo=owner-source/repo-source --limit 30
```

### Step 2: Understand Source Architecture

```bash
# Get source README for feature context
gh api repos/owner-source/repo-source/readme --jq '.content' | base64 -d

# Get source documentation
gh api repos/owner-source/repo-source/contents/docs --jq '.[].name'
gh api repos/owner-source/repo-source/contents/README.md --jq '.content' | base64 -d

# Get example usage
gh api repos/owner-source/repo-source/contents/examples --jq '.[].download_url'
gh api repos/owner-source/repo-source/contents/tests --jq '.[].name'
```

### Step 3: Analyze Target Repo

```bash
# Get target repo structure
gh api repos/owner-target/repo-target/git/trees/HEAD?recursive=1 --paginate -q '.tree[] | select(.type=="blob") | .path' | head -100

# Get existing patterns in target
gh api repos/owner-target/repo-target/contents/src --jq '.[].name'
gh api api repos/owner-target/repo-target/contents/lib --jq '.[].name'

# Get package/dependency files
gh api repos/owner-target/repo-target/contents/package.json --jq '.content' | base64 -d
gh api repos/owner-target/repo-target/contents/requirements.txt --jq '.content' | base64 -d
gh api repos/owner-target/repo-target/contents/go.mod --jq '.content' | base64 -d

# Check for similar features already implemented
gh search code "equivalent feature" --repo=owner-target/repo-target --limit 20
```

### Step 4: Find API/Library Equivalences

```bash
# Source dependencies
gh api repos/owner-source/repo-source/contents/package.json --jq '.content' | base64 -d | jq '.dependencies'
gh api repos/owner-source/repo-source/contents/requirements.txt --jq '.content' | base64 -d

# Target dependencies
gh api repos/owner-target/repo-target/contents/package.json --jq '.content' | base64 -d | jq '.dependencies'

# Find equivalent libraries via web search
websearch_web_search_exa("Python equivalent of lodash JavaScript")
websearch_web_search_exa("Go equivalent of React hooks")
```

### Step 5: Map Data Structures

```bash
# Get source data models
gh api repos/owner-source/repo-source/contents/src/models --jq '.[].download_url'
gh api repos/owner-source/repo-source/contents/src/types --jq '.[].download_url'

# Get target data models
gh api repos/owner-target/repo-target/contents/src/models --jq '.[].name'
gh api repos/owner-target/repo-target/contents/src/types --jq '.[].name'
```

## Feature Mapping Output Format

### Feature Translation Report

```markdown
# 功能转译报告: [功能名称]

## 源项目
- **名称**: source-repo
- **URL**: github.com/owner-source/source-repo
- **分支**: main
- **源文件**: `src/features/feature-name/`

## 目标项目
- **名称**: target-repo
- **URL**: github.com/owner-target/target-repo
- **分支**: main
- **目标路径**: `src/features/feature-name/`

## 功能概述

### 源项目实现
描述该功能在源项目中是如何实现的，包括：
- 核心算法/逻辑
- 数据流
- API 接口
- 依赖的外部库

### 功能入口点
```python
# 源: src/feature/main.py
def process(data):
    ...
```

## API 映射表

| 源项目 API | 目标项目等效 | 说明 |
|-----------|-------------|------|
| `source.func()` | `target.func()` | 直接等价 |
| `source.API.post()` | `target.API.create()` | 命名不同，功能相同 |
| `source.Lodash.groupBy()` | `target.toolz.groupby()` | 不同库的等价实现 |

## 数据结构映射表

| 源项目数据结构 | 目标项目数据结构 | 说明 |
|---------------|-----------------|------|
| `class User` | `class User` | 结构相同 |
| `dict` | `TypedDict` | Python 3.8+ 类型化字典 |
| `JSON Object` | `Pydantic Model` | 带验证的等价物 |

## 依赖映射表

| 源项目依赖 | 目标项目依赖 | 说明 |
|-----------|-------------|------|
| `lodash` | `toolz` | Python 函数式工具库 |
| `axios` | `httpx` | 异步 HTTP 客户端 |
| `react-query` | `swr` | 数据获取 hooks |

## 实现步骤

### 步骤 1: 环境准备
```bash
# 安装目标项目依赖
pip install equivalent-package

# 创建功能目录
mkdir -p src/features/feature-name
```

### 步骤 2: 数据模型
```python
# 目标: src/features/feature-name/models.py
from typing import TypedDict
from datetime import datetime

class FeatureInput(TypedDict):
    name: str
    value: int

class FeatureOutput(TypedDict):
    id: str
    result: bool
    timestamp: datetime
```

### 步骤 3: 核心逻辑
```python
# 目标: src/features/feature-name/service.py
from .models import FeatureInput, FeatureOutput

async def process_feature(input: FeatureInput) -> FeatureOutput:
    """
    转译自源: source-repo/src/feature/processor.py::process()
    
    逻辑对应:
    - 源: input validation -> process -> format output
    - 目标: 使用 target-repo 的中间件进行验证
    """
    # 1. 验证输入 (使用 target-repo 验证中间件)
    validated = await validate_input(input)
    
    # 2. 核心处理 (对应源 process() 函数)
    result = await core_processing(validated)
    
    # 3. 格式化输出
    return format_output(result)
```

### 步骤 4: API 端点
```python
# 目标: src/features/feature-name/routes.py
from fastapi import APIRouter

router = APIRouter()

@router.post("/feature")
async def create_feature(data: FeatureInput) -> FeatureOutput:
    """对应源: POST /api/features"""
    return await process_feature(data)
```

### 步骤 5: 测试
```python
# 目标: tests/features/feature-name/test_service.py
import pytest
from src.features.feature_name.service import process_feature

async def test_process_feature():
    input_data = {"name": "test", "value": 42}
    result = await process_feature(input_data)
    assert result["id"] is not None
    assert result["result"] == True
```

## 关键差异与注意事项

### 命名差异
- 源: `getUserById()` → 目标: `get_user_by_id()`
- 源: `userId` → 目标: `user_id`

### 范式差异
- 源: 命令式编程 → 目标: 函数式/响应式编程
- 源: 同步 → 目标: 异步优先

### 边界情况
1. **空值处理**: 源使用 `|| {}` 默认值，目标使用 `dict.get()`
2. **错误处理**: 源使用回调，目标使用异常/Result 类型
3. **类型安全**: 源使用 JSDoc，目标使用 TypeScript/Pydantic

## 验证清单

- [ ] 核心功能逻辑已转译
- [ ] API 接口签名匹配
- [ ] 数据模型字段对应
- [ ] 依赖包已安装
- [ ] 单元测试通过
- [ ] 集成测试通过
- [ ] 文档已更新

## 资源链接

- 源项目: github.com/owner-source/source-repo
- 目标项目: github.com/owner-target/target-repo
- 相关讨论: (搜索到的 Issue/PR 链接)
```

## Quick Translation Commands

```bash
# Compare file structures
echo "Source structure:" && gh api repos/owner-source/repo-source/contents/src --jq '.[].name'
echo "Target structure:" && gh api repos/owner-target/repo-target/contents/src --jq '.[].name'

# Get source implementation
gh api repos/owner-source/repo-source/contents/src/feature.py --jq '.content' | base64 -d

# Search for patterns in target
gh search code "similar pattern" --repo=owner-target/repo-target --limit 10

# Find example usage in source
gh search code --filename=test --repo=owner-source/repo-source --match=file "feature_name" --limit 10
```

## Translation Patterns

### API Pattern Translation

| Source Pattern | Target Pattern | Example |
|---------------|----------------|---------|
| `axios.get(url)` | `httpx.get(url)` | HTTP GET |
| `fetch(url, options)` | `requests.get(url, **kwargs)` | HTTP with options |
| `Promise.then(cb)` | `asyncio await` | Async handling |
| `callback(err, result)` | `try/except` | Error handling |

### Data Structure Translation

| Source Structure | Target Structure | Notes |
|-----------------|-----------------|-------|
| `class Foo {}` | `class Foo:` | Python class |
| `interface Bar {}` | `TypedDict` or `dataclass` | Type definitions |
| `{key: value}` | `dict` or `pydantic model` | Objects |
| `[...array]` | `list(...)` | Arrays |
| `Set([...])` | `set([...])` | Unique collections |

### Framework Pattern Translation

| Source | Target | Notes |
|--------|--------|-------|
| React Hook | Vue Composition API | Similar reactive patterns |
| Express middleware | FastAPI middleware | Different middleware style |
| Django ORM | SQLAlchemy | Different ORM patterns |
| Go goroutines | Python asyncio | Concurrent execution |

## Important Notes

- Always verify API signatures match semantic behavior, not just names
- Consider idiomatic patterns in target language/framework
- Check for built-in equivalents before adding dependencies
- Test edge cases that may differ between implementations
- Consider performance characteristics of different approaches
- Document any intentional deviations from source behavior
- Get feedback from target project maintainers if unsure
