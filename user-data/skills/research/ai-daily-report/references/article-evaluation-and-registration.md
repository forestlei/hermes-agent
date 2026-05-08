# Article Evaluation & GitHub Memory Registration Pipeline

> Established 2026-05-06, updated through 10-article evaluation sessions (World2VLM/ragWiki/open-slide/Hermes Curator/MetaCompress/Tolaria/Impeccable + 3 earlier)

## Full Pipeline (when user shares an article link)

### Step 1: Fetch Article Content
- **Toutiao articles** (`m.toutiao.com/article/XXX`): Use `browser_navigate` → `browser_snapshot` (scroll down for full content)
- **When browser_snapshot truncates** (shows "[... N more lines truncated]"): Use `browser_console` with `document.querySelector('article')?.innerText || document.querySelector('main')?.innerText` to extract full article text in one call. This is more reliable than scrolling+snapshotting for long articles.
- **Toutiao videos** (`m.toutiao.com/w/XXX`): Same method, but content is in og:title + image text only — low information density
- **Other platforms**: Use `urllib` with mobile UA

### Step 2: Verify Claims via GitHub/arXiv
For every project/paper mentioned in the article:
1. **GitHub verification**: `curl -s "https://api.github.com/repos/{owner}/{repo}"` — verify stars, language, license, description
2. **GitHub search** (if exact repo unknown): `curl -s "https://api.github.com/search/repositories?q={name}&sort=stars&per_page=5"`
3. **arXiv verification**: `curl -s "https://arxiv.org/abs/{id}"` — check paper exists and title matches
4. **Cross-reference README**: For coding tools, fetch README to verify benchmark claims

### Step 3: 4-Dimension Quality Score (each 0-25, total 0-100)

| Dimension | Max | What to check |
|-----------|-----|---------------|
| **Accuracy** | 25 | Do the numbers match GitHub/arXiv? Are claims verifiable? Any fabrication? |
| **Depth** | 25 | Architecture-level analysis or just feature list? Missing core innovations? |
| **Originality** | 25 | Independent testing/analysis or just README translation? |
| **Readability** | 25 | Clear structure? Misleading analogies? Selective data presentation? |

**Thresholds**: ≥80 达标 (register source) | 70-79 跟踪 | <70 未达标

### Step 4: Register Qualifying Projects to github-memory
If the article features a GitHub project worth tracking:

```python
# Tier rules:
# ⭐≥500 → tier=standard (正式录入)
# ⭐≥200 (技能类/学术类放宽) → tier=tracked (跟踪)
# ⭐<200 → tier=watching (仅关注)

# Create metadata.json
metadata = {
    "full_name": "owner/repo",
    "stars": actual_stars,  # from GitHub API, NOT article claim
    "language": "...",
    "description": "...",
    "feature_tags": [...],  # include L-layer tags (L2/L3/L5/L7)
    "tier": "standard|tracked|watching",
    "tracking_rule": "skills-project: standard at ≥500, promote at ...",
    "source": "toutiao-article-{author}-{date}",
    "added_date": "YYYY-MM-DD",
    "key_features": [...]
}
```

Write to: `~/.hermes/github-memory/{topic}/{owner}/{repo}/metadata.json`

### Step 5: Update Indexes & Sync
1. Add repo to `~/.hermes/github-memory/_index.yaml` under appropriate topic
2. Update `~/.hermes/github-memory/_features/tag-index.json` with new tags
3. Run: `bash ~/.hermes/scripts/auto-sync-data.sh "register: {repo}"`

### Step 6: Structure Knowledge for Agent Framework (when user requests)
When user says "作为辅助知识输入" or similar:
- Create a structured knowledge file at `~/.hermes/github-memory/_knowledge/{topic}.md`
- Include: comparison matrices, selection criteria, key technical differences
- This knowledge becomes searchable by the agent framework

## Common Red Flags (Updated 2026-05-06, from 10-article evaluation session)

### Tier-1 Red Flags (accuracy -10~-15, immediate disqualification consideration)
1. **Fabricated CLI parameters/config keys** — Article invents flags/keys that don't exist in the actual tool. Example: Hermes Curator article claimed `--force` and `--dry-run` flags (actual: only `--sync`); claimed config keys `schedule/auto_merge/pin_protection` (actual: only `enabled`). **Detection**: Run `tool --help` and `tool config` against actual installed tool.
2. **Fabricated project name** — Article renames a real project to a fictional name, making it impossible for readers to find. Example: NovelClaw renamed to "Novel-Free" (GitHub search returns 0 results). **Detection**: Search GitHub for exact quoted project name.
3. **Fabricated technical concepts** — Article claims architectural patterns that don't exist in the project. Example: open-slide article claimed "LangGraph式多节点编排" (project has zero LangGraph/orchestration content). **Detection**: grep README for claimed keywords.
4. **Star count concealment** — Article says "暂未公开具体星数" or "GitHub ⭐ 星标" without giving the number, when actual stars are very low (2⭐). **Detection**: Always check GitHub API for actual stargazers_count.
5. **Ecology attribution fraud** — Unrelated "撞名" projects claimed as part of known ecosystems. (Already in main SKILL.md red flags section)
6. **主仓库星标嫁接 (Sub-component star attribution fraud)** — Article uses the parent monorepo's star count for a specific plugin/skill/sub-component that has no independent repo. Example: voice-call article claimed "336K⭐" / "35万+" for what is actually a single SKILL.md file inside the openclaw/openclaw repo (369K⭐). The voice-call "project" has no independent existence. **Detection**: Check if the GitHub URL's repo contains the "project" as a sub-directory. If `curl -sL` follows a redirect to a different repo, the original name was likely a codename/old name. Verify repo contents — if only 1 file (SKILL.md/README.md) exists at the claimed path, it's a sub-component, not an independent project. Penalty: accuracy -10~-15, flag "主仓库星标嫁接".

### Tier-2 Red Flags (accuracy -5~-8)
5b. **Code not released** — Article describes a paper's GitHub project as if code is available, but the repo only contains a README saying "code coming soon" or "being organized". Common with CVPR/NeurIPS/ICML papers. **Detection**: Check repo contents via GitHub API (`/repos/{owner}/{repo}/contents/`) — if only README.md exists, code is not released. Flag as "代码未发布" and note in evaluation. Penalty: accuracy -3~-5 (not as severe as fabrication, but misleading omission).
6. **Fabricated API examples** — Code examples that don't match actual API. Example: open-slide article showed `createPresentation({topic, agent, style})` JS function (actual API: `npx @open-slide/cli init` CLI command). **Detection**: Check actual package exports vs article code.
7. **Benchmark claims without data** — "比传统PPT工具快10倍" with zero supporting data. **Detection**: Search for benchmark tables/comparisons in README.
8. **Exaggerated maturity** — Phase 1/walking skeleton project described as "核心功能已实现落地". **Detection**: Check .planning/ directory, project phases, README maturity indicators.
9. **Exaggerated team size** — 1 contributor described as "开发者团队保持高频更新". **Detection**: Check GitHub contributors API.
10. **Self-evolution framing** — Maintenance tool (skill pruning/merging) described as "自我进化/自己迭代自己". **Detection**: Read actual tool description carefully — "prunes stale, consolidates overlaps, archives obsolete" ≠ "evolution".

### Tier-3 Red Flags (accuracy -3~-5)
11. **Unsupported local model claims** — Article claims "支持Ollama/LM Studio" but README only says "works with any coding agent". **Detection**: Search README for specific model names.
12. **AI-generated images** — Toutiao flags "图片疑似AI生成，请注意甄别". Reduce readability score.
13. **No GitHub link** — Article says "去GITHUB下载吧" without providing URL. **Detection**: Check if article contains any clickable GitHub URL.
14. **Marketing exaggeration** — 2⭐ project called "颠覆神器", maintenance tool called "觉醒/横空出世". **Detection**: Compare article framing with actual project maturity/stars.
15. **Project name misspelling** — Article consistently uses wrong project name (e.g., "impactable" instead of "impeccable"). This is NOT fabrication (author genuinely got it wrong) but makes the article unsearchable. **Detection**: If GitHub search for article's name returns 0 relevant results, try fuzzy matching or search by description/features. Penalty: accuracy -8~-12 (readers literally cannot find the project).
16. **License omission (AGPL-3.0)** — Article describes project as "完全开源且永久免费" without mentioning AGPL-3.0 commercial use restrictions. AGPL requires anyone providing network services based on the code to also open-source their modifications. **Detection**: Check `license` field in GitHub API response. If AGPL-3.0, flag the omission. Penalty: accuracy -3~-5 (misleading for developer readers).
17. **High typo density** — Multiple typos in technical terms (e.g., "TypeSript"→TypeScript, "前段"→前端, "熟套"→俗套, "cri"→CLI). 3+ typos in a short article signals "口播稿转文字" quality with no editorial review. **Detection**: Count technical term misspellings. Penalty: readability -3~-5.
18. **Self-contradictory star claims** — Title says "35万+" but body says "336.0K" (both wrong). Signals zero editorial review. **Detection**: Compare all star count mentions in article. Penalty: accuracy -5 (on top of any star fraud penalty).
19. **Micro-toutiao format limitations** — 微头条 (/w/ URLs) are short-form posts with content in images, low text density. Expect lower depth scores (12-16 range typical). Don't penalize accuracy for brevity, but depth ceiling is ~18/25 for this format.

## Common Red Flags (from 10-article evaluation sessions, 2026-05-06)

| Red Flag | Detection | Penalty |
|----------|-----------|---------|
| **Benchmark without conditions** | "5x faster" but no hardware/model/concurrency specified | accuracy -5 |
| **Selective data presentation** | Best-case numbers only (e.g., "local embedding off" mode) | accuracy -3 |
| **Concept substitution** | "启动快245倍" implying "编码快245倍"; maintenance tool called "自我进化" | accuracy -5~-8 |
| **Missing core innovations** | Article covers performance but ignores Swarm/Memory/Self-Dev | depth -8 |
| **Code not released** | Repo only has README ("code coming soon") but article implies code is available | accuracy -3~-5 |
| **Star count mismatch** | Article says "近4千" but actual is 4195 (acceptable) or "33万" but actual is 33K (10x fraud) | accuracy -10~-15 |
| **主仓库星标嫁接** | Sub-component (single file in monorepo) presented as independent project with parent repo's stars | accuracy -10~-15 |
| **Star count concealment** | "暂未公开具体星数" when actual stars are 2 — deliberate hiding of low popularity | accuracy -10 |
| **Ecology attribution fraud** | Unrelated project claimed as part of known ecosystem | accuracy -15 |
| **Fabricated CLI parameters** | Article shows `--force`, `--dry-run` flags that don't exist in actual `--help` | accuracy -8~-10 |
| **Fabricated config keys** | Article invents config.yaml keys (schedule, auto_merge, pin_protection) not in actual config | accuracy -8 |
| **Fabricated API examples** | Article shows `createPresentation()` JS function but actual API is CLI command | accuracy -5~-8 |
| **Fabricated technical concepts** | "LangGraph式多节点编排" when project has zero LangGraph/orchestration content | accuracy -10 |
| **Video format** | Low information density, can't verify claims | depth -10 |
| **Marketing exaggeration** | 2⭐ project called "颠覆神器"; Phase 1 walking skeleton called "核心功能已实现落地" | accuracy -8~-13 |
| **Project name misspelling** | Article uses wrong name consistently (e.g., "impactable" vs "impeccable") — readers can't find the project | accuracy -8~-12 |
| **License omission (AGPL-3.0)** | "完全开源且永久免费" without mentioning AGPL commercial restrictions | accuracy -3~-5 |
| **High typo density** | 3+ technical term typos → "口播稿转文字" quality, no editorial review | readability -3~-5 |

## Advanced Verification Techniques

### Technique: Run actual CLI commands (for installed tools)
When an article covers a tool you have installed on your system, verify claims by running the actual commands:
1. `tool --help` — check if claimed flags/parameters actually exist
2. `tool status` — verify claimed features and current state
3. `tool config` — check if claimed config keys exist
4. Compare article's code examples against actual API/CLI

**Example**: Hermes Curator article claimed `--force` and `--dry-run` flags. Running `hermes curator run --help` revealed only `--sync` exists. Article also claimed config keys `schedule/auto_merge/pin_protection` — running `hermes config set curator.enabled true` confirmed only `enabled` is a real key.

### Technique: Verify project maturity claims
When article claims "核心功能已实现落地" or "具备极高的实用价值":
1. Check `.planning/` directory for phase status (walking skeleton ≠ production-ready)
2. Check contributors count (1 contributor ≠ "开发者团队")
3. Check project age (3 days ≠ "高频更新")
4. Check forks/subscribers (0/0 ≠ community validation)

### Technique: Cross-reference README for fabricated concepts
When article claims specific architectural patterns:
1. `grep -iE '(keyword)' README.md` — search for claimed concepts
2. If zero matches, flag as fabricated technical concept
3. Check pyproject.toml/package.json for claimed dependencies

### Technique: Cross-reference README for fabricated concepts
When article claims specific architectural patterns or technical concepts:
1. `curl -s 'https://raw.githubusercontent.com/{owner}/{repo}/{branch}/README.md' | grep -iE '(keyword1|keyword2)'` — search for claimed keywords
2. If zero matches, flag as fabricated technical concept (accuracy -10)
3. Also check package exports vs article code examples — fabricated API calls are common

### Technique: Verify project name existence
When article names a project that you can't find on GitHub:
1. Search with exact quotes: `curl -s 'https://api.github.com/search/repositories?q=%22{project-name}%22'`
2. If total_count = 0, the name may be fabricated, renamed, or misspelled
3. Try broader search with key features to find the real project
4. Example: "Novel-Free" → 0 results, but "novel + LLM + generation + long + story" → found NovelClaw
5. **For misspelled names**: Try searching by article's description keywords + sort=stars. The real project usually appears in top results. Example: "impactable + design + skill" → found pbakaus/impeccable (25K⭐). Compare article features against top results' README to confirm match.

### Technique: Verify star count (always)
1. `curl -s 'https://api.github.com/repos/{owner}/{repo}'` → check `stargazers_count`
2. Compare with article's claim:
   - Concealment ("暂未公开具体星数") → usually very low stars, flag as red flag
   - Underestimate (article says 17K, actual 23.6K) → note but not penalized
   - Overestimate (10x magnification pattern) → accuracy -10~-15, flag "星标数量级误读"
3. Apply tier rules: ≥500 → standard, ≥200 (skills) → tracked, ≥20 (academic) → tracked

### Technique: Verify project maturity
When article claims "核心功能已实现落地" or "高频更新":
1. Check `.planning/` directory for phase status
2. Check `CLAUDE.md` or `PROJECT.md` for current development stage
3. Check contributors count (1 contributor ≠ "开发者团队")
4. Check commit frequency (20 total commits ≠ "高频更新")

### Technique: Follow GitHub 301 redirects to find actual repo
When `curl -s "https://api.github.com/repos/{owner}/{repo}"` returns stars=N/A or appears empty:
1. The repo may have been renamed/transferred — GitHub API returns 301 redirect
2. Use `curl -sL` (follow redirects) instead of `curl -s` to get the actual repo data
3. Example: `steipete/clawdis` → 301 → `openclaw/openclaw` (369K⭐). The old name was a codename that got merged into the main repo.
4. This also reveals **star attribution fraud**: article may use the main repo's stars for a sub-component (see "主仓库星标嫁接" red flag below).

### Technique: Detect sub-component star attribution fraud
When article claims high star count for a specific plugin/skill/feature:
1. Check if the GitHub URL points to a **sub-directory** of a larger project (e.g., `openclaw/openclaw/skills/voice-call/`)
2. If yes, the stars belong to the **parent repo**, not the sub-component
3. Verify by checking the repo contents: if the "project" is just a single SKILL.md or config file inside a monorepo, it has no independent star count
4. Common pattern: OpenClaw skills, Claude Code skills — these are files within 300K+⭐ repos but have zero independent following
5. Penalty: accuracy -10~-15, flag "主仓库星标嫁接" (distinct from "星标数量级误读" which is about 10x number misreading)

### Technique: Verify code availability (academic papers)
When article covers an academic paper with a GitHub link:
1. Check repo contents: `curl -s "https://api.github.com/repos/{owner}/{repo}/contents/" | python3 -c "import sys,json; items=json.load(sys.stdin); [print(f'{i[\"name\"]} ({i[\"type\"]})') for i in items]"`
2. If only README.md exists → code not released. Check README for "coming soon" / "being organized" language.
3. This is common for top-venue papers (CVPR/NeurIPS/ICML) where code release lags paper publication by months.
4. Flag in evaluation: "GitHub仓库代码未发布，文章未标注此状态" — accuracy -3~-5 for omission.

### Technique: Evaluate pure technical articles (no GitHub/arXiv project)
When article is an original technical piece with no specific project/paper to verify:
1. **Verify technology stack claims** — Check if mentioned libraries/tools actually exist (e.g., owlready2 on PyPI, LangChain on GitHub)
2. **Evaluate code quality** — If article includes code snippets, check for correctness (syntax, API usage, logic)
3. **Assess conceptual accuracy** — TBox/ABox distinction, OWL semantics, etc. — verify against known definitions
4. **No star count to verify** — Skip GitHub verification, focus on accuracy of technical claims and depth of analysis
5. **Scoring adjustment**: Accuracy can still be high (20-25) if technical claims are correct, even without a project to verify. Depth and Originality become the primary differentiators.

### Technique: Detect self-contradictory star claims
When article contains multiple star count claims that contradict each other:
1. Compare title claim vs body claim (e.g., title says "35万+" but body says "336.0K")
2. Both may be wrong — verify against GitHub API
3. Self-contradiction is a strong signal of low editorial quality
4. Penalty: accuracy -5 for contradiction on top of any star count fraud penalty

### Technique: Detect "开源" mislabeling for paid-MCP-wrapper projects
When article claims a project is "开源" or "open source":
1. Check if the code is open-source (Apache-2.0, MIT, etc.) — this part may be true
2. **Check the .mcp.json or connectors** — are they local processes or remote HTTP endpoints to paid SaaS?
3. If all MCP connectors point to `https://vendor.com/mcp` URLs requiring paid API keys/subscriptions, the **core value is closed-source and paid**, even if the wrapper code is open
4. Common with vendor agent templates (Anthropic financial-services, etc.)
5. Penalty: accuracy -5~-8 for "开源" claim without qualifying that data sources are paid; accuracy -10~-15 for "开箱即用" claim when connectors cost $10K+/year
6. Flag: "开源误导：代码开源但核心数据源闭源付费"

### Technique: Detect training vs inference concept confusion
When article claims "1秒训练" or "instant training" for a model:
1. Check if the model actually **trains** (gradient updates, backpropagation) or does **in-context learning / inference** (no weight updates)
2. TabPFN, ICL-based methods, and prompt-based approaches do NOT train — they predict at inference time
3. Confusing "训练" (training) with "推理/预测" (inference/prediction) is a fundamental conceptual error
4. This is worse than a number mismatch — it misrepresents the core innovation of the project
5. Penalty: accuracy -5~-8 for conceptual confusion
6. Flag: "训练/推理概念混淆"

### Technique: Detect version number fabrication
When article claims a specific version number (e.g., "v1.9.1"):
1. Check GitHub releases API: `curl -s "https://api.github.com/repos/{owner}/{repo}/releases"` — empty array = no releases
2. Check tags: `curl -s "https://api.github.com/repos/{owner}/{repo}/tags"` — empty array = no tags
3. Check README for version strings — compare with article's claim
4. Pattern: Small projects (≤10⭐) claiming v1.x+ are almost always inflated. Real v1.0+ implies API stability and feature completeness.
5. Penalty: accuracy -10~-15 for version inflation ≥3x

### Technique: Verify claimed tech stack against dependency files
When article claims "基于X+Y" (e.g., "基于langgraph+langchain"):
1. Check requirements.txt: `curl -s "https://api.github.com/repos/{owner}/{repo}/contents/requirements.txt" | jq -r '.content' | base64 -d`
2. Check pyproject.toml: `curl -s "https://api.github.com/repos/{owner}/{repo}/contents/pyproject.toml" | jq -r '.content' | base64 -d`
3. Check package.json for JS projects
4. If claimed framework has ZERO mentions in any dependency file → fabricated tech stack
5. This is distinct from "fabricated technical concepts" — it's specifically about claiming a tech stack that doesn't exist in the build configuration
6. Penalty: accuracy -10~-15 (core architectural claim is false)

### Technique: Verify "开源" claims via LICENSE file
When article calls a project "开源" or "open source":
1. `curl -s "https://api.github.com/repos/{owner}/{repo}" | jq '.license'` — if null, there is NO license
2. No license = default copyright = all rights reserved = NOT open source (legally)
3. Public repo ≠ open source. Anyone can view the code, but cannot legally use/modify/distribute it
4. Penalty: accuracy -5~-8 for calling an unlicensed repo "开源"

### Technique: Detect self-promotional articles (自宣稿)
When article reads like a product announcement for a small project:
1. Compare toutiao author name with GitHub project owner — "星穹科技" ≈ xiafanli (same person)
2. Check project stars — 8⭐ projects don't get independent media coverage
3. Check article date vs project creation date — article published same week as first commit = self-promotion
4. Pattern: Author describes features as if already implemented, but PROJECT_MODULES.md shows them as "进行中/待增强"
5. Flag as "自宣稿" — informational value exists (knowing what's being built) but accuracy is compromised by self-interest
6. Penalty: depth -5~-10 (no independent analysis or critical evaluation)

### Technique: Detect "全栈国产化" false claims
When article claims "全栈国产化" or "自主可控":
1. Check dependencies in requirements.txt, package.json, pyproject.toml
2. If the project depends on LangChain, Docker, Python ecosystem, React, etc. — these are NOT domestic/国产 technologies
3. "国产化" claims for projects built on foreign open-source stacks are misleading
4. Penalty: accuracy -5~-8
5. Flag: "全栈国产化误导"

### Technique: Detect maturity misrepresentation
When article claims "不是demo" or "生产级" or "真正能用":
1. Check README for maturity indicators: "Research Preview", "alpha", "beta", "experimental"
2. Check if sub-features are marked as "preview" (e.g., "subagent delegation is a preview capability")
3. Article claiming production-readiness when the project itself says "Research Preview" is a maturity misrepresentation
4. Penalty: accuracy -3~-5
5. Flag: "成熟度夸大：项目标注Research Preview但文章称生产级"

## New Red Flags (2026-05-07 session, from TabPFN/ScienceClaw/Anthropic金融/MetricBot evaluations)

| Red Flag | Detection | Penalty |
|----------|-----------|---------|
| **"开源" mislabeling (paid MCP wrappers)** | Code is open-source but ALL MCP connectors point to paid SaaS HTTP endpoints ($10K+/year) | accuracy -5~-8 for "开源"; -10~-15 for "开箱即用" |
| **训练/推理概念混淆** | Article says "1秒训练" but model does in-context learning (no training at all) | accuracy -5~-8 |
| **全栈国产化误导** | Claims "自主可控" but depends on LangChain/Docker/Python (foreign stack) | accuracy -5~-8 |
| **成熟度夸大** | Article says "不是demo/生产级" but README says "Research Preview" | accuracy -3~-5 |
| **工具数量夸大** | Claims 3000+ tools but README says 1900+ (58% inflation) | accuracy -5~-10 |
| **"全面超越"无基准** | Claims "全面超越X/Y" with zero benchmark data or comparison methodology | accuracy -10~-15 |
| **版本号虚标** | Article claims v1.9.1 but actual is v0.3.0 (6x inflation); no releases/tags exist. Check GitHub releases API and README version strings | accuracy -10~-15 |
| **技术栈虚构** | Article claims "基于langgraph+langchain" but requirements.txt/pyproject.toml have ZERO such dependencies. Always verify claimed tech stack against actual dependency files | accuracy -10~-15 |
| **No LICENSE ≠ 开源** | Code is publicly visible on GitHub but has NO LICENSE file. Legally = all rights reserved = NOT open source. `curl -s "https://api.github.com/repos/{owner}/{repo}" | jq '.license'` returns null | accuracy -5~-8 |
| **桌面版/下载版虚构** | Claims "Windows桌面版下载" but no Electron/Tauri dependency, no releases, no desktop packaging exists | accuracy -10~-15 |
| **自宣稿检测** | Toutiao author name matches/relates to GitHub project owner. Article is essentially a promotional piece for own low-star project. Check if author name ≈ GitHub username/org | flag as "自宣稿", depth -5~-10 |

## Cross-Topic Linking (2026-05-07)

When evaluating an article, consider whether the project/concept has cross-topic relevance beyond its primary topic assignment. Document these links in the evaluation output.

**Example**: SkillRouter (skill routing for LLM agents) → primary topic: 智能体项目. But its core finding (progressive disclosure = information loss) is isomorphic to knowledge compilation's core problem (compiling away body → metadata loses distinguishing signal). This links it to 本体与语义's knowledge compilation sub-topic at L3 level.

## Topic Assignment Guide

| Project Type | github-memory Topic |
|-------------|-------------------|
| Coding agent / Agent framework | 智能体项目 |
| Inference engine / Model serving | AI基础设施 |
| Skills / Tools / Resources | 工具与资源 |
| Research paper (with code) | AI研究 |
| Application platform | AI应用平台 |
| Data engineering | 数据工程AI项目 |
| Ontology / Semantic web / Knowledge engineering | 本体与语义 |
| Knowledge compilation (classic: SDD/d-DNNF/PC) | 本体与语义 |
| Knowledge compilation (LLM-era: wiki/KB builders) | 本体与语义 + 工具与资源 |
| Knowledge compilation (skill: conversation→skill) | 智能体项目 |

## Knowledge Compilation Concept Isomorphisms (for article evaluation)

When evaluating articles about ML/AI systems, watch for conceptual isomorphisms with knowledge compilation that can enrich the analysis:

| ML Concept | Knowledge Compilation Analog | Explanation |
|------------|---------------------------|-------------|
| TabPFN (in-context learning) | L1 classic KC (SDD/d-DNNF) | Pre-training = compile-time; inference = runtime query; both trade upfront cost for polynomial-time queries |
| TabPFN 50K data limit | Circuit size limit | SDD/d-DNNF have circuit complexity limits; TabPFN has data size limits — same fundamental constraint |
| SkillRouter (progressive disclosure) | KC information loss | Compiling away body → metadata loses distinguishing signal = progressive disclosure information loss |
| LLM knowledge bases (WeKnora) | L2 KC (doc→structured KB) | Document compilation into queryable knowledge structures |

These isomorphisms add depth to evaluations and help identify cross-topic relevance for github-memory registration.
