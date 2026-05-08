---
name: skill-portability-pattern
version: "1.0"
description: Pattern for making Hermes skills portable to other AI agents. Tool mapping, config decoupling, adapter code.
---

# 技能通用移植模式

## 问题
Hermes技能中硬编码了工具名（read_file/search_files/execute_code等）和配置系统（config.yaml key），导致无法直接移植到其他Agent。

## 解决方案

### 1. 工具映射表（必须）
创建抽象工具层，映射到具体Agent的工具：

| 抽象工具 | Hermes | Claude Code | Codex | Generic |
|----------|--------|-------------|-------|---------|
| file_read | read_file | Read | read | open() |
| file_write | write_file | Write | write | open('w') |
| file_search | search_files | Grep | grep | grep/ripgrep |
| shell_exec | execute_code | Bash | shell | subprocess |
| web_search | web_search | WebSearch | search | requests |
| web_fetch | web_extract | WebFetch | fetch | urllib |
| browser | browser_navigate | — | — | selenium |
| memory | memory | — | — | json file |
| todo | todo | TodoRead/Write | — | json file |

### 2. 最低工具集声明
明确声明运行该技能最少需要哪些工具：
```
最低工具集：file_read + file_write + file_search + shell_exec
```

### 3. 配置去耦合
- Hermes config key → 环境变量（WIKI_PATH, WIKI_DOMAIN等）
- 在技能开头声明所需环境变量

### 4. Python适配器代码
提供4函数最小实现，复制即用：
```python
def file_read(path): return open(path).read()
def file_write(path, content): open(path,'w').write(content)
def file_search(pattern, directory): subprocess.run(['grep','-rn',pattern,directory],capture_output=True)
def shell_exec(cmd): subprocess.run(cmd, shell=True, capture_output=True)
```

### 5. 移植指南结构
- 目标平台列表
- 每个平台的适配步骤
- 验证清单

## 已应用
- llm-wiki v4.1.0 portable版（42.2KB，飞书已发送）
