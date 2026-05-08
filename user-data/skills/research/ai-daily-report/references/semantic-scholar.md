### Semantic Scholar Integration for Paper Ranking & Survey Detection (NEW — Critical)

**Purpose:** Dynamically query S2 at report generation time to:
1. **Detect surveys/reviews** — S2 `publicationTypes` field contains `['Review']` for authoritative survey classification
2. **Adjust ranking** — `referenceCount` and `citationCount` provide quality signals beyond heuristic scoring
3. **Identify influential papers** — `influentialCitationCount` surfaces papers cited by other highly-cited works

**API endpoint (batch POST — most efficient):**
```
POST https://api.semanticscholar.org/graph/v1/paper/batch?fields=externalIds,title,citationCount,referenceCount,influentialCitationCount,publicationTypes,venue
Body: {"ids": ["ArXiv:2604.08224", "ArXiv:2604.09459", ...]}
```

**Rate limits:** S2 is VERY aggressive with 429 errors. Rules:
- Use batch POST endpoint (1 request for up to 50 papers) — NOT individual lookups
- Add 5-second delay before S2 API call (let any previous rate limit cool down)
- If batch returns 429, skip S2 enrichment entirely and use heuristic scores only
- Maximum 1 batch call per report generation (don't retry on failure)
- For weekly reports with many papers, split into batches of 15 with 3s delays

**Survey detection logic (3-tier):**
1. **S2 `publicationTypes` contains `'Review'`** → 📋 CONFIRMED SURVEY (highest confidence)
2. **Title contains survey keywords** AND `referenceCount > 30` → 📋 LIKELY SURVEY
   - Keywords: `survey`, `review`, `unified`, `comprehensive`, `taxonomy`, `sok`, `systematization`, `state-of-the-art`, `overview`, `landscape`, `a primer`, `foundations of`, `towards a`
3. **`referenceCount > 60`** alone → 📋 POSSIBLE SURVEY (lower confidence, may be long empirical paper)

**Ranking adjustment rules:**
- Confirmed survey (S2 `Review` type): quality_score = max(quality_score, 80) — surveys always featured
- Likely survey (title keywords + refs>30): quality_score += 5
- `citationCount > 0`: quality_score += min(10, citationCount)
- `influentialCitationCount > 0`: quality_score += min(10, influentialCitationCount * 3)
- `referenceCount > 40` (non-survey): quality_score += 2 (thorough related work = quality signal)

**Integration in daily report:**
- Surveys get a **dedicated section** `## 📋 综述专题` BEFORE the regular paper section
- Survey table includes: arXiv ID, 中文译名, 作者单位, referenceCount, S2 type
- Top 3 surveys get deep analysis (same 4-dimension format as regular papers)
- Regular paper section excludes surveys (no duplication)

**Example S2 batch response:**
```json
[
  {"externalIds": {"ArXiv": "2604.08224"}, "title": "...", "citationCount": 0, "referenceCount": 0, "publicationTypes": ["Review"], "venue": ""},
  {"externalIds": {"ArXiv": "2604.09459"}, "title": "...", "citationCount": 0, "referenceCount": 63, "publicationTypes": ["Review"], "venue": ""}
]
```

**Collection code (add to Phase 1 after paper merge):**
```python
import urllib.request, ssl, json, re, time

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

# Load merged papers
with open(f"{DATA_DIR}/papers.json") as f:
    papers = json.load(f)

# Collect arXiv IDs (strip version suffix)
arxiv_ids = []
for p in papers[:30]:  # Top 30 candidates only
    aid = p.get('arxiv_id_normalized', p.get('arxiv_id', ''))
    aid = re.sub(r'v\d+$', '', aid)
    if aid:
        arxiv_ids.append(aid)

# S2 batch lookup
time.sleep(5)  # Rate limit cooldown
body = json.dumps({"ids": [f"ArXiv:{aid}" for aid in arxiv_ids]})
url = "https://api.semanticscholar.org/graph/v1/paper/batch?fields=externalIds,title,citationCount,referenceCount,influentialCitationCount,publicationTypes,venue"
headers = {"User-Agent": "Mozilla/5.0", "Content-Type": "application/json"}

try:
    req = urllib.request.Request(url, data=body.encode(), headers=headers, method="POST")
    with urllib.request.urlopen(req, timeout=20, context=ctx) as resp:
        s2_data = json.loads(resp.read().decode('utf-8'))
    
    # Build S2 lookup
    s2_lookup = {}
    for p in s2_data:
        if not p: continue
        ext = p.get('externalIds') or {}
        aid = ext.get('ArXiv', '')
        if aid:
            s2_lookup[aid] = {
                'citationCount': p.get('citationCount', 0) or 0,
                'referenceCount': p.get('referenceCount', 0) or 0,
                'influentialCitationCount': p.get('influentialCitationCount', 0) or 0,
                'publicationTypes': p.get('publicationTypes') or [],
                'venue': p.get('venue', '') or ''
            }
    
    # Enrich papers with S2 data
    SURVEY_KEYWORDS = ['survey', 'review', 'unified', 'comprehensive', 'taxonomy', 'sok', 'systematization', 'state-of-the-art', 'overview', 'landscape', 'a primer', 'foundations of', 'towards a']
    
    for p in papers:
        aid = re.sub(r'v\d+$', '', p.get('arxiv_id_normalized', p.get('arxiv_id', '')))
        if aid in s2_lookup:
            s2 = s2_lookup[aid]
            p['s2_citationCount'] = s2['citationCount']
            p['s2_referenceCount'] = s2['referenceCount']
            p['s2_influentialCitationCount'] = s2['influentialCitationCount']
            p['s2_publicationTypes'] = s2['publicationTypes']
            p['s2_venue'] = s2['venue']
            
            # Survey detection
            is_s2_review = 'Review' in s2['publicationTypes']
            title_lower = p.get('title', '').lower()
            has_survey_kw = any(kw in title_lower for kw in SURVEY_KEYWORDS)
            is_likely_survey = has_survey_kw and s2['referenceCount'] > 30
            is_possible_survey = s2['referenceCount'] > 60
            
            if is_s2_review:
                p['is_survey'] = 'confirmed'
                p['quality_score'] = max(p.get('quality_score', 50), 80)
            elif is_likely_survey:
                p['is_survey'] = 'likely'
                p['quality_score'] = p.get('quality_score', 50) + 5
            elif is_possible_survey:
                p['is_survey'] = 'possible'
                p['quality_score'] = p.get('quality_score', 50) + 2
            else:
                p['is_survey'] = 'no'
            
            # Ranking adjustment
            p['quality_score'] = min(100, p['quality_score'] + 
                min(10, s2['citationCount']) + 
                min(10, s2['influentialCitationCount'] * 3) +
                (2 if s2['referenceCount'] > 40 and p.get('is_survey') == 'no' else 0))
    
    print(f"S2 enrichment: {len(s2_lookup)} papers enriched")
    surveys = [p for p in papers if p.get('is_survey') in ('confirmed', 'likely')]
    print(f"Surveys detected: {len(surveys)} (confirmed={len([p for p in surveys if p['is_survey']=='confirmed'])}, likely={len([p for p in surveys if p['is_survey']=='likely'])})")
    
except Exception as e:
    print(f"S2 enrichment failed: {str(e)[:80]} — using heuristic scores only")

# Save enriched papers
with open(f"{DATA_DIR}/papers.json", 'w') as f:
    json.dump(papers, f, indent=2, ensure_ascii=False)
```
