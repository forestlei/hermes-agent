# Toutiao Ecology Attribution Fraud Cases

> Verified cases where Chinese tech media (今日头条/知乎) falsely attributed projects to well-known AI Agent ecosystems.

## Confirmed Fraud Cases

### 1. rusty_hermes → Falsely attributed to Hermes Agent ecosystem
- **GitHub**: rust-hermes/rusty_hermes (72⭐, Rust)
- **Actual**: Rust bindings for Meta/React Native's **Hermes JavaScript engine** (facebook/hermes)
- **Article claimed**: "Hermes Agent JS引擎的Rust封装，广泛用于Rust环境中嵌入AI逻辑层"
- **Evidence of fraud**: Description says "Rust bindings for the Hermes JavaScript engine" — zero mention of Hermes Agent or Nous Research
- **Source**: facebook/hermes/discussions/1324 confirms it's about the JS engine

### 2. hermes-five → Falsely attributed to Hermes Agent ecosystem
- **GitHub**: dclause/hermes-five (36⭐, Rust)
- **Actual**: Independent **Robotics & IoT Platform** ("The Rust Robotics & IoT Platform")
- **Article claimed**: "机器人与IoT专用版，提供Rust异步API，类似带大脑的Johnny-Five"
- **Evidence of fraud**: Description mentions "Robotics & IoT Platform" — zero mention of Hermes Agent
- **Note**: The name similarity comes from Johnny-Five (JS robotics framework), not Hermes Agent

### 3. hermes-go → Falsely attributed to Hermes Agent ecosystem
- **GitHub**: Harsh-2909/hermes-go (25⭐, Go)
- **Actual**: Independent **AI Agent framework in Go** ("An AI Agent framework in Go for building Agents with RAG, Knowledge, Memory, Tools")
- **Article claimed**: "模块化框架，受LangChain启发，为Go开发者提供多模态支持"
- **Evidence of fraud**: Description mentions "AI Agent framework" but zero mention of Hermes Agent or Nous Research. It's an independent framework that happens to use the name "hermes"

### 4. awesome-hermes-agent → Misrepresented as "multi-agent collaboration framework"
- **GitHub**: 0xNyk/awesome-hermes-agent (2,508⭐)
- **Actual**: A **curated awesome list** of skills/tools/integrations for Hermes Agent
- **Article claimed**: "多代理协作框架，包含17个专业代理，通过结构化接口进行复杂代码工程任务的协作"
- **Evidence of fraud**: It's a LIST, not a framework. The "17 agents" likely refers to items in the list, not a software architecture.

## Language Label Fraud

### 5. nullclaw → Labeled as Rust, actually Zig
- **GitHub**: nullclaw/nullclaw (7,405⭐, **Zig**)
- **Article claimed**: Listed under "Rust开发项目" section
- **Actual**: Description explicitly says "written in Zig"
- **Impact**: The article's entire "Rust ecosystem" categorization is undermined

## Pattern Recognition

### How to detect ecology attribution fraud:
1. **Read the actual GitHub description** — does it mention the claimed ecosystem?
2. **Check README for ecosystem keywords** — search for "OpenClaw", "Hermes Agent", "Nous Research" etc.
3. **Verify via GitHub topics** — legitimate ecosystem projects typically tag themselves
4. **Cross-reference with official docs** — does the ecosystem's official site list this project?

### Common fraud patterns:
- **Name collision**: Projects named "hermes-*" that have nothing to do with Hermes Agent (the name "hermes" is extremely common — Greek god, JS engine, IoT platform, etc.)
- **Aspirational attribution**: Articles want to create a "high-performance ecosystem matrix" narrative, so they round up any project with a related name
- **Feature inflation**: Awesome lists get rebranded as "frameworks", small utilities become "platforms"

### Statistical baseline from this session:
- 10 projects in a "high-performance ecosystem matrix" article
- 3/10 (30%) ecology attribution fraud
- 1/10 (10%) language label fraud
- 1/10 (10%) feature description fraud
- 5/10 (50%) under 100 stars
- **Only 2/10 had >1K stars** (nullclaw 7.4K, awesome-hermes-agent 2.5K)
- **0/10 suitable as execution platform** — all were Agent frameworks or misattributed projects
