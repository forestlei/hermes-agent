## Source Verification & Traceability System

### Problem: AI Hallucination Risk

AI-generated content in reports may contain fabricated claims. This verification system distinguishes verifiable raw data from AI interpretations, ensuring every claim is traceable to its source.

### Four-Level Verification System

| Level | Mark | Meaning | Example |
|-------|------|---------|---------|
| **L1 Raw Data** | `[✓]` | Directly from API/original source, verifiable | Paper title, author list, GitHub stars |
| **L2 Cross-Verified** | `[✓✓]` | Confirmed by 2+ independent sources | Same paper found on both arXiv and Semantic Scholar |
| **L3 AI Interpretation** | `[~]` | AI-generated from source material, not independently verified | "Key contribution", "Why important" |
| **L4 Unverified** | `[?]` | No original source supports this claim | Impact prediction, trend speculation |

### Verification Rules by Content Type

**Papers:**
- Title, authors, citation count, arXiv ID → `[✓]` (from arXiv/S2 API)
- Abstract translation/paraphrase → `[~]` (must reference original abstract)
- "Key contributions" → `[~]` (MUST quote specific sentences from abstract/paper, with paragraph reference)
- "Potential impact" → `[?]` (speculative, always mark as unverified)

**GitHub Projects:**
- Stars, description, language, topics → `[✓]` (from GitHub API)
- "Why trending" → `[~]` (MUST reference specific README section, commit message, or issue)
- "Competitor comparison" → `[?]` (unless directly stated in project docs)

**News/Blogs:**
- Title, source, date → `[✓]` (from RSS/API)
- Content summary → `[~]` (must reference original article paragraphs)
- "Impact analysis" → `[?]` (speculative)

**User-Shared Articles:**
- Original article content (fetched) → `[✓]`
- AI quality scoring → `[~]` (subjective assessment)

### Traceability Requirements

Every `[~]` claim MUST include one of:
1. **Direct quote** from source material with location reference (e.g., "Abstract para 2", "README §Features")
2. **Source URL** pointing to the specific page/section
3. **Data reference** (e.g., "S2 citation count: 45 as of 2026-04-12")

Any `[~]` claim without traceability is automatically downgraded to `[?]`.

### Report Visual Indicators

In delivered reports, each item shows its verification level:
- `[✓]` — Reliable, directly sourced
- `[✓✓]` — Cross-verified by multiple sources
- `[~]` — AI interpretation, see traceability note
- `[?]` — Unverified claim, use with caution

Example in report:
```markdown
**[✓] Scaling Laws for Neural Language Models** — Kaplan et al.
- [✓] Authors: Jared Kaplan, Sam McCandlish...
- [✓] Citations: 3,240 (Semantic Scholar, 2026-04-12)
- [~] Key contribution: "Loss scales as a power-law with model size" (Abstract para 1)
- [?] Potential impact: May reshape how labs allocate compute budgets
```

### Pre-Delivery Verification Audit

Before delivering any report, run this mandatory audit:

1. **Traceability check**: Every `[~]` claim must have a source reference. Missing → downgrade to `[?]`
2. **L1 data validation**: All API-sourced data (titles, stars, citations) must match the stored raw collection data
3. **Cross-reference**: Major claims should appear in 2+ sources. Single-source claims get `[?]` not `[~]`
4. **Unverified ratio**: If `[?]` claims exceed 30% of total claims, add ⚠️ warning at report top:
   ```
   > ⚠️ 本报告含较多未验证推测 (XX% [?] 标记)，请谨慎参考
   ```
5. **Metadata storage**: Store verification levels in each item's metadata.json:
   ```json
   {
     "verification": {
       "title": {"level": "L1", "source": "arxiv-api"},
       "key_contribution": {"level": "L3", "source": "abstract-para2", "quote": "..."},
       "impact_prediction": {"level": "L4", "source": null}
     }
   }
   ```

### Verification Enhancement Actions

When a `[?]` or `[~]` claim is important enough to upgrade:
1. **Fetch original source** — Use `web_extract` or `curl` to get the primary source
2. **Find supporting evidence** — Search for the claim in other sources
3. **Upgrade verification level** — If confirmed by original source: `[?]` → `[~]`; if cross-verified: `[~]` → `[✓✓]`
4. **Update metadata** — Record the verification upgrade with evidence
