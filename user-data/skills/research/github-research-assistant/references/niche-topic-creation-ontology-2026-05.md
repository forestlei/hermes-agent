# 本体与语义 Topic Creation (2026-05-07)

## Context
User shared 5 Toutiao articles for evaluation. One article about "本体(Ontology) + Agent" scored 83/100 (达标). User corrected: "本体是有专题的，这个领域论文和项目都少，技术文章也需要纳入" — meaning niche domains need articles registered too, not just projects/papers.

## Topic Creation Process
1. **Check existing topics** — Confirmed github-memory had no 本体/Ontology topic
2. **Search for related projects** — GitHub API searches: `ontology OWL reasoner`, `ontology agent LLM`, `owlready2 semantic-web`, `knowledge-graph ontology construction`
3. **Register existing knowledge** — 2 papers from prior sessions (OntoKG, AdaPGC) + 1 article (本体Agent, 83分)
4. **Register discovered projects** — 5 projects: open-ontologies(92⭐), automatic-KG-creation-with-LLM(341⭐), pygraft(702⭐), ummon(37⭐), Cortex(13⭐)
5. **Create _index.yaml entry** — Added "本体与语义" topic with description emphasizing niche nature
6. **Sync** — `auto-sync-data.sh "新增本体与语义专题：8个条目(2论文+1文章+5项目)"`

## Article metadata.json template for niche topics
```json
{
  "full_name": "ontology-agent-article",
  "type": "article",
  "title": "AI-Agent 本体让"听懂业务"并"按规矩办事"",
  "author": "Allen",
  "platform": "toutiao",
  "date": "2026-05",
  "url": "https://m.toutiao.com/article/7630712695121117723/",
  "score": 83,
  "description": "...",
  "tags": ["ontology", "OWL", "agent", "语义层", "规则推理", "TBox", "ABox", "owlready2", "HermiT", "知识工程"],
  "key_insights": ["..."],
  "tech_stack": ["LangChain", "PostgreSQL", "owlready2", "HermiT", "OWL", "Protégé", "OpenAI"],
  "related_papers": [],
  "related_projects": ["owlready2", "LangChain"]
}
```

## Key observations
- Niche domain projects have very low stars (max 702⭐ for pygraft, most <100)
- High-quality technical articles (≥80 score) are MORE valuable than low-star projects in niche domains
- The article scored 83 while the best project scored only 72 (AdaPGC paper) — articles can outrank projects
- When creating a niche topic, proactively search GitHub for related projects even if none appeared in the evaluated articles
- OWL/ontology ecosystem is fragmented: tools (owlready2, HermiT, Protégé) are mature but niche; agent+ontology integration is emerging (open-ontologies as MCP server, Cortex as OWL-RL+SPARQL)