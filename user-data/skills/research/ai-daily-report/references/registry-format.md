### Source Registry v2 Format

The `shared/sources/registry.json` uses a v2 format with author-level granularity and multi-dimension scoring:

```json
{
  "version": 2,
  "updated": "YYYY-MM-DD",
  "sources": {
    "platform-author-name": {
      "name": "作者名",
      "platform": "今日头条/微信公众号/知乎/B站/...",
      "author_url": "作者主页URL",
      "category": "AI科普/AI学术/AI产业/...",
      "quality_score": {
        "total": 82,
        "accuracy": 84,
        "depth": 80,
        "originality": 82,
        "readability": 85
      },
      "description": "简要描述其内容特点",
      "added_date": "YYYY-MM-DD",
      "notable_articles": [...]
    }
  },
  "projects": {
    "project-id": {
      "name": "项目名",
      "github": "GitHub URL or null",
      "demo": "Demo URL or null",
      "website": "Website URL or null",
      "stars": 53441,
      "category": "AI预测/群体智能仿真/...",
      "description": "项目描述",
      "tech_stack": ["Vue", "Python", "..."],
      "key_features": ["feature1", "feature2"],
      "use_cases": ["use case1", "use case2"],
      "added_date": "YYYY-MM-DD",
      "source_article": "来源文章URL"
    }
  }
}
```

**Key rules:**
- Sources are keyed by `platform-author-name` (e.g., `toutiao-feiyudi`)
- Each source MUST have `author_url` pointing to the specific author's page
- `quality_score` is an object with `total` + 4 sub-dimensions
- Projects live in a separate `projects` key — they can overlap with sources (same item in both) without conflict
- Projects are keyed by a slug (e.g., `mirofish`, `ai-scientist-v2`)
