---
name: fact-check
description: "Verify information legitimacy and trace provenance. Cross-reference claims against multiple sources, assess credibility, detect bias, and auto-register high-value high-credibility sources. Use when: (1) ingesting new information that needs verification, (2) checking a claim's legitimacy, (3) tracing where information came from, (4) detecting bias or single-source dependency, (5) auto-discovering credible sources from provenance chains."
version: 1.0.0
---

# Fact Check — 信息溯源与合法性验证

Verify information legitimacy, trace provenance chains, and auto-discover high-value sources.

## Core Principle

**No information enters the knowledge base without provenance.** Every claim must be traceable to its origin, and high-credibility sources discovered during verification are automatically registered.

## Workflow

### 1. Provenance Tracing (溯源)

When ingesting a source, trace the full chain:

```
原始作者 → 发布平台 → 发现方式 → 发现者 → 入库时间
```

**For each piece of information, record:**

| Field | Description | Example |
|-------|-------------|---------|
| `original_url` | Where it was first published | `https://arxiv.org/abs/2604.11784` |
| `author` | Original author/creator | `Karpathy` |
| `author_url` | Author's profile | `https://twitter.com/karpathy` |
| `platform` | Publishing platform | `arxiv`, `twitter`, `github` |
| `discovered_via` | How we found it | `shared-by-user`, `rss`, `cross-ref` |
| `discovered_from` | Which source led us here | `user-wechat-share` |
| `discovered_at` | When we found it | `2026-04-15T08:07:18Z` |
| `share_chain` | Propagation path | `[user→rss→article]` |

**Provenance quality scoring:**

| Chain | Score | Trust Level |
|-------|-------|-------------|
| Author's official channel | 1.0 | 🟢 Highest |
| Peer-reviewed (arxiv/conf) | 0.9 | 🟢 High |
| Reputable media (Reuters/FT) | 0.85 | 🟢 High |
| Domain expert's blog | 0.75 | 🟡 Good |
| Community aggregation (HN/Reddit) | 0.6 | 🟡 Moderate |
| Social media post | 0.4 | 🟠 Low |
| Anonymous/unknown | 0.2 | 🔴 Unreliable |

### 2. Cross-Reference Verification (交叉验证)

**A claim is credible when confirmed by 2+ independent sources.**

```
Claim → Search wiki for same claim → Search external sources → Assess agreement
```

**Verification levels:**

| Level | Criteria | Action |
|-------|----------|--------|
| ✅ **Verified** | 2+ independent sources agree | Accept, mark verified |
| ⚠️ **Plausible** | 1 source + no contradiction | Accept with caveat |
| ❌ **Disputed** | Sources contradict | Flag, note both positions |
| 🚫 **Unverifiable** | No way to confirm | Mark unverified, low confidence |
| 🔴 **Retracted** | Original source retracted | Remove or mark retracted |

**Cross-reference sources:**

1. **Internal** — Search existing wiki pages for the same claim
2. **Author's other works** — Does the author consistently make this claim?
3. **Peer sources** — Do other credible sources in the same domain agree?
4. **Opposing sources** — Do any sources contradict? If so, why?

### 3. Credibility Assessment (可信度评估)

**Per-source credibility score (0-1):**

```
credibility = provenance_quality × 0.3
            + source_reliability × 0.25
            + cross_ref_count × 0.2
            + author_authority × 0.15
            + recency × 0.1
```

| Factor | Weight | How Measured |
|--------|--------|-------------|
| Provenance quality | 30% | Chain score from Step 1 |
| Source reliability | 25% | Historical accuracy (from source-evolution) |
| Cross-reference count | 20% | Number of independent confirmations |
| Author authority | 15% | Tier from source-evolution (S/A/B/C/D) |
| Recency | 10% | How recent (decay over 90 days) |

**Credibility thresholds:**

| Score | Label | Action |
|-------|-------|--------|
| ≥ 0.8 | 🟢 High credibility | Accept + auto-register source |
| 0.5-0.8 | 🟡 Moderate | Accept with verification flag |
| 0.3-0.5 | 🟠 Low | Accept only with user confirmation |
| < 0.3 | 🔴 Unreliable | Reject or quarantine |

### 4. Bias Detection (偏见检测)

**Single-source dependency check:**

For each wiki page, check:
- How many independent sources contribute? (≥3 is healthy)
- Are all sources from the same platform/author? (bias risk)
- Do sources represent diverse viewpoints? (echo chamber risk)

**Bias indicators:**

| Indicator | Risk | Action |
|-----------|------|--------|
| Only 1 source | 🔴 High | Flag for additional sources |
| All sources same platform | 🟠 Medium | Note platform bias |
| All sources same author | 🔴 High | Flag author dependency |
| No opposing viewpoints | 🟡 Medium | Note one-sided coverage |
| ≥3 diverse sources | 🟢 Low | Healthy coverage |

### 5. Auto-Source Discovery (自动发现高价值源)

**During provenance tracing, auto-register sources that meet criteria:**

**Auto-register when:**
- Source credibility ≥ 0.8
- Source is a new domain not yet covered
- Source provides unique perspective (diversity score high)
- Author is Tier S or A (from source-evolution)

**Auto-register flow:**

```
溯源发现新URL → 评估可信度 → 检查是否已有 → 
  如果可信度≥0.8且未注册 → 
    注册到source-evolution → 
    记录发现链到wiki/log.md
```

**What gets auto-registered:**

| Discovered | Criteria | Auto-register? |
|------------|----------|----------------|
| Author's official blog | Tier S/A author | ✅ Yes |
| Peer-reviewed paper | arxiv/conf | ✅ Yes |
| Reputable media article | Reuters/FT/Bloomberg | ✅ Yes |
| Domain expert's Twitter | 10k+ followers, verified | ✅ Yes |
| Random social media post | Low followers | ❌ No |
| Marketing/promotional content | Commercial bias | ❌ No |
| Duplicate of existing source | Already in wiki | ❌ No |

### 6. Compliance Check (合规检查)

**Copyright check:**
- arxiv papers → ✅ Open access
- GitHub repos → ✅ Check license field
- News articles → ⚠️ Excerpt only, link to original
- Social media posts → ⚠️ Public posts only
- Paywalled content → ❌ Don't store full text

**Data retention:**
- Raw sources: Keep indefinitely (immutable)
- Verification status: Re-verify every 90 days
- Retracted content: Move to `_archive/` immediately
- Stale content: Flag when >90 days without update

### 7. SIFT Verification Method (from source-verification skill)

**S - Stop**: 不要立即分享或使用未验证的信息
**I - Investigate the source**: 谁是信息背后的来源？
**F - Find better coverage**: 其他可靠源怎么说？
**T - Trace claims**: 找到声明的原始来源

#### Social Media Account Verification

| 检查项 | 说明 |
|--------|------|
| 账号年龄 | 老账号更可信 |
| 发帖模式 | 突然活跃=可疑 |
| 粉丝质量 | 真人vs机器人 |
| 内容原创性 | 只转发=低可信 |
| 认证状态 | 官方认证加分 |

**Red flags:** 新号+大胆声明、话题突然转向、协同行为、头像为图库照片

#### Reverse Image Search
1. Google Images / TinEye / Yandex Images
2. EXIF元数据检查（时间、设备、GPS）
3. 内容分析（天气、阴影、标识是否匹配）
4. 找最早出现位置

#### Video Verification
1. 技术分析：分辨率、音画同步、编辑痕迹
2. 内容分析：地点、时间指示、天气匹配
3. 元数据：上传日期vs声称事件日期
4. 工具：InVID/WeVerify、YouTube DataViewer

### 8. Provenance Lineage Tracing (from provenance skill)

Given `/fact-check lineage <artifact>`:

1. **Read artifact** → 查找provenance元数据（source refs, session IDs, dates）
2. **Trace source chain** → `grep -i "source\|session\|from\|extracted" <artifact>`
3. **Search session transcripts** → 找到该信息何时被讨论
4. **Build lineage report** → 完整谱系：原始源→中间处理→当前状态
5. **Find orphans** → 孤立引用（指向不存在的源）
6. **Find stale citations** → 过时引用（源已更新但引用未更新）

Output: lineage report with full chain + orphan detection + staleness alerts

### 9. Source Credibility Checklist (from source-verification skill)

#### Basic Identification
- [ ] 全名/组织可识别
- [ ] 联系方式可验证
- [ ] 专业资质可查
- [ ] 线上存在跨平台一致

#### Expertise Assessment
- [ ] 对声称领域有相关专业知识
- [ ] 该领域有业绩记录
- [ ] 同行认可
- [ ] 无传播虚假信息历史

#### Motivation Analysis
- [ ] 潜在利益冲突
- [ ] 财务利益？
- [ ] 政治或意识形态动机？
- [ ] 个人恩怨？

#### Corroboration
- [ ] 声明可独立验证？
- [ ] 其他可信源确认？
- [ ] 有文件证据？
- [ ] 有矛盾源？

## Integration with Other Skills

### llm-wiki Integration

During ingest, fact-check runs automatically:

```
llm-wiki ingest → fact-check provenance → fact-check verify → 
  if verified → ingest into wiki + auto-register sources
  if disputed → flag in frontmatter + alert user
  if unreliable → quarantine in _unverified/
```

**Frontmatter fields added by fact-check:**

```yaml
provenance:
  original_url: ...
  author: ...
  platform: ...
  discovered_via: ...
  share_chain: [...]

verification:
  status: verified|unverified|disputed|retracted
  confidence: 0.0-1.0
  cross_refs: N
  fact_check: pending|passed|failed
  last_verified: YYYY-MM-DD
  verified_by: [source-ids]
```

### source-evolution Integration

When fact-check discovers a high-credibility source:

```typescript
// Auto-register to source-evolution
evolution.registerSource({
  url: discoveredUrl,
  name: discoveredName,
  type: inferredType,
  tier: inferredTier,  // from credibility score
  reliability: credibilityScore
});
```

**Feedback loop:**

```
source-evolution provides reliability scores → 
  fact-check uses them for credibility assessment → 
    fact-check discovers new high-value sources → 
      auto-register back to source-evolution
```

## Commands

### Verify a specific claim

```
/fact-check verify "claim text"
```

1. Search wiki for matching claims
2. Search external sources
3. Assess agreement
4. Report verification status

### Trace provenance

```
/fact-check trace <page-name>
```

1. Read page frontmatter
2. Follow provenance chain
3. Report full trace with quality scores

### Audit wiki credibility

```
/fact-check audit
```

1. Scan all wiki pages
2. Check verification status
3. Flag unverified/disputed/retracted
4. Check single-source dependency
5. Check bias indicators
6. Report summary with recommendations

### Auto-discover sources

```
/fact-check discover
```

1. Scan recent wiki ingests
2. Extract provenance chains
3. Identify high-credibility sources not yet registered
4. Auto-register to source-evolution
5. Report new sources added

## Lint Integration

Add these checks to llm-wiki lint:

| Check | Severity | Description |
|-------|----------|-------------|
| Missing provenance | Error | Page has no provenance fields |
| Unverified claims | Warning | Page has verification.status = unverified |
| Single-source pages | Warning | Page relies on only 1 source |
| Stale verification | Info | verification.last_verified > 90 days ago |
| High bias risk | Info | All sources from same platform/author |
| Retracted content | Error | verification.status = retracted |

## Scaling

- **Verification cache**: Store verification results in `.cache/verification.db` (SQLite)
- **Re-verification interval**: 90 days for verified, 30 days for unverified
- **Batch verification**: Verify multiple claims in one pass
- **Incremental audit**: Only check pages changed since last audit

## Extended Commands (fused from provenance + source-verification)

- `/fact-check sift <url>` — SIFT method verification (Stop→Investigate→Find→Trace)
- `/fact-check lineage <artifact>` — Deep lineage with orphan/stale detection

## Fused Skill Dependencies

- **provenance** (boshu2/agentops) → lineage tracing, orphan detection
- **source-verification** (jamditis/claude-skills-journalism) → SIFT method, digital verification

## Author Tracking Rules (v1.1 - 2026-04-16)

When ingesting an article, always:

1. **Extract author** from article metadata (byline, __INITIAL_STATE__, meta tags)
2. **Register author as information source** with fields:
   - name, platform, follower_count, verified_status, expertise_area
3. **Cross-platform author matching**:
   - Search same author name on other platforms (WeChat, Weibo, Toutiao, Twitter)
   - Compare content similarity (topic, style, expertise area)
   - Match confidence: same-name + same-topic + same-style = high (0.9), same-name + same-topic = medium (0.7), same-name only = low (0.4)
4. **Record match evidence** in provenance.cross_platform_sources
5. **Update source-evolution** with author profile and cross-platform links

### Author → WeChat Matching Process

```
头条号作者 → Exa搜索 "作者名 site:mp.weixin.qq.com" → 
  找到同名号 → 比较内容主题/风格 → 
    高匹配 → 标记为同一作者(0.9)
    中匹配 → 标记为可能同一作者(0.7)
    低匹配 → 标记为不同作者(0.4)
```
