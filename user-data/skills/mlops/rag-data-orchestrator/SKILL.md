---
name: rag-data-orchestrator
version: 1.0.0
description: RAG数据预处理编排层——统一调度专业解析器(Docling/Marker/Firecrawl/Crawl4AI/Zerox等)，提供数据清洗总入口，支持质量断言、冲突检测、多平台输出适配
triggers:
  - RAG数据预处理
  - 数据清洗管道
  - 文档解析编排
  - 知识库构建
  - 数据质量检查
  - document preprocessing pipeline
  - RAG data cleaning
  - knowledge base ingestion
---

# RAG Data Orchestrator — 数据清洗总入口

## 核心定位

**不是又一个解析器，而是解析器的调度者。**

本技能解决的核心问题：RAG数据预处理领域有大量专业解析器（Docling做PDF、Firecrawl做Web、Marker做PDF→MD、Zerox做OCR），但缺少一个**编排层**来：
1. 根据输入类型自动选择最优解析器
2. 统一输出格式，适配下游平台（LangChain/LlamaIndex/Chroma/直接API）
3. 对解析结果做质量断言和冲突检测
4. 提供一键式总入口，而非手动串联多个工具

## 架构

```
┌─────────────────────────────────────────────────┐
│           rag-data-orchestrator                  │
│         (统一入口 + 质量保障 + 格式适配)          │
├─────────────────────────────────────────────────┤
│  1. Source Detection    — 自动识别输入类型        │
│  2. Parser Selection    — 选择最优解析器          │
│  3. Quality Assertion   — 数据质量断言            │
│  4. Conflict Detection  — 多源冲突检测            │
│  5. Output Adaptation   — 多平台格式适配          │
├─────────────────────────────────────────────────┤
│  Parser Plugins (可插拔)                         │
│  ┌─────────┐ ┌─────────┐ ┌──────────┐          │
│  │ Docling  │ │ Marker  │ │ Firecrawl│          │
│  │ (PDF)   │ │(PDF→MD) │ │  (Web)   │          │
│  └─────────┘ └─────────┘ └──────────┘          │
│  ┌─────────┐ ┌─────────┐ ┌──────────┐          │
│  │Crawl4AI │ │  Zerox  │ │Unstruct- │          │
│  │ (Web)   │ │  (OCR)  │ │  ured    │          │
│  └─────────┘ └─────────┘ └──────────┘          │
│  ┌─────────┐ ┌─────────┐ ┌──────────┐          │
│  │  Skill  │ │ Custom  │ │  Any     │          │
│  │ Seekers │ │ Plugin  │ │  Parser  │          │
│  └─────────┘ └─────────┘ └──────────┘          │
├─────────────────────────────────────────────────┤
│  Output Adaptors                                 │
│  LangChain | LlamaIndex | ChromaDB | FAISS |    │
│  Qdrant | Weaviate | Pinecone | Markdown | JSON │
└─────────────────────────────────────────────────┘
```

## 解析器选择策略

### 按输入类型的默认最优解析器

| 输入类型 | 首选解析器 | 备选 | 选择理由 |
|---------|-----------|------|---------|
| PDF(学术论文) | Docling | Marker | Docling表格/公式提取最强，IBM维护 |
| PDF(文档→Markdown) | Marker | Docling | Marker专注PDF→MD转换，格式保真度高 |
| PDF(扫描件/图片) | Zerox | Unstructured | Zerox用GPT-4V做OCR，扫描件效果最好 |
| Web(静态页面) | Crawl4AI | Firecrawl | Crawl4AI免费开源，静态页面足够 |
| Web(SPA/JS渲染) | Firecrawl | Crawl4AI+Playwright | Firecrawl自带JS渲染 |
| Web(批量爬取) | Firecrawl | Crawl4AI | Firecrawl批量爬取+结构化提取一体化 |
| Office(docx/pptx/xlsx) | Unstructured | Docling | Unstructured Office格式支持最全 |
| 代码仓库 | Skill Seekers AST | 自定义 | Skill Seekers的AST解析+冲突检测独特 |
| 混合多源 | 编排层自动调度 | — | 按源类型分派最优解析器，合并结果 |
| 未知/通用 | Unstructured | Docling | Unstructured覆盖面最广 |

### 选择逻辑

```python
PARSER_PRIORITY = {
    "pdf_academic": ["docling", "marker", "unstructured"],
    "pdf_to_markdown": ["marker", "docling", "unstructured"],
    "pdf_scanned": ["zerox", "unstructured"],
    "web_static": ["crawl4ai", "firecrawl"],
    "web_spa": ["firecrawl", "crawl4ai"],
    "web_batch": ["firecrawl", "crawl4ai"],
    "office": ["unstructured", "docling"],
    "code": ["skill_seekers", "custom"],
    "mixed": ["orchestrator"],
    "unknown": ["unstructured", "docling"],
}

def select_parser(source_type, subtype=None, available=None):
    key = f"{source_type}_{subtype}" if subtype else source_type
    priority = PARSER_PRIORITY.get(key, PARSER_PRIORITY.get(source_type, ["unstructured"]))
    if available:
        for p in priority:
            if p in available:
                return p
        return available[0]
    return priority[0]
```

## 安装与依赖

### 核心依赖（按需安装，不是全部必须）

| 解析器 | 安装命令 | 必需环境变量 | 说明 |
|--------|---------|-------------|------|
| Docling | `pip install docling` | 无 | PDF学术论文首选 |
| Marker | `pip install marker-pdf` | 无 | PDF→Markdown首选 |
| Crawl4AI | `pip install crawl4ai` | 无 | Web静态页面首选(免费) |
| Firecrawl | `pip install firecrawl-py` | FIRECRAWL_API_KEY | Web SPA/批量爬取 |
| Zerox | `pip install py-zerox` | OPENAI_API_KEY | OCR扫描件 |
| Unstructured | `pip install "unstructured[all-docs]"` | 无 | 通用fallback |

**最少只需安装1个解析器即可使用。** 推荐：Docling(PDF) + Crawl4AI(Web) + Unstructured(通用)

### 检测已安装解析器

```python
def detect_available_parsers():
    """检测当前环境中可用的解析器"""
    available = {}
    parsers = {
        "docling": {"import_name": "docling", "pip_name": "docling", "env_var": None},
        "marker": {"import_name": "marker", "pip_name": "marker-pdf", "env_var": None},
        "crawl4ai": {"import_name": "crawl4ai", "pip_name": "crawl4ai", "env_var": None},
        "firecrawl": {"import_name": "firecrawl", "pip_name": "firecrawl-py", "env_var": "FIRECRAWL_API_KEY"},
        "zerox": {"import_name": "py_zerox", "pip_name": "py-zerox", "env_var": "OPENAI_API_KEY"},
        "unstructured": {"import_name": "unstructured", "pip_name": "unstructured[all-docs]", "env_var": None},
    }
    for name, info in parsers.items():
        try:
            __import__(info["import_name"])
            env_ok = True
            if info["env_var"]:
                import os
                env_ok = bool(os.getenv(info["env_var"]))
            available[name] = {"installed": True, "env_ready": env_ok, "pip_name": info["pip_name"]}
        except ImportError:
            available[name] = {"installed": False, "env_ready": False, "pip_name": info["pip_name"]}
    return available
```

## 使用流程

### Step 1: 检测环境

```bash
# 查看已安装的解析器
rag-orchestrator doctor
```

### Step 2: 单源处理

```bash
# PDF学术论文 → 自动选择Docling
rag-orchestrator process paper.pdf --type pdf_academic

# PDF扫描件 → 自动选择Zerox
rag-orchestrator process scan.pdf --type pdf_scanned

# 网页 → 自动选择Crawl4AI
rag-orchestrator process https://example.com --type web

# 强制指定解析器
rag-orchestrator process doc.pdf --parser marker

# 指定输出格式
rag-orchestrator process doc.pdf --output langchain
rag-orchestrator process doc.pdf --output llama-index
rag-orchestrator process doc.pdf --output chroma
rag-orchestrator process doc.pdf --output markdown
```

### Step 3: 多源编排

```bash
# 混合源处理（配置文件方式）
rag-orchestrator pipeline --config pipeline.yaml
```

```yaml
# pipeline.yaml 示例
name: my-knowledge-base
sources:
  - path: ./papers/
    type: pdf_academic
    parser: docling        # 显式指定，或留空自动选择
    
  - path: https://docs.example.com
    type: web_static
    parser: crawl4ai
    
  - path: ./scanned-reports/
    type: pdf_scanned
    parser: zerox

quality:
  min_chunk_length: 50
  max_chunk_length: 1000
  deduplicate: true
  conflict_detection: true

output:
  format: langchain
  path: ./processed/
```

### Step 4: 质量断言

```python
QUALITY_RULES = {
    "min_chunk_length": 50,       # 过短的chunk无检索价值
    "max_chunk_length": 1000,     # 过长的chunk影响检索精度
    "no_empty_chunks": True,
    "no_duplicate_chunks": True,
    "encoding_check": True,       # 检测乱码
    "table_preservation": True,   # 表格结构保持检查
    "code_block_integrity": True, # 代码块完整性检查
}

def assert_quality(chunks, rules=None):
    """对解析结果执行质量断言"""
    rules = rules or QUALITY_RULES
    results = {"total_chunks": len(chunks), "passed": 0, "failed": 0, "issues": []}
    for i, chunk in enumerate(chunks):
        issues = []
        text = chunk.get("text", chunk.get("content", ""))
        if rules["no_empty_chunks"] and not text.strip():
            issues.append("empty_chunk")
        if rules["min_chunk_length"] and len(text) < rules["min_chunk_length"]:
            issues.append("too_short")
        if rules["max_chunk_length"] and len(text) > rules["max_chunk_length"]:
            issues.append("too_long")
        if rules["encoding_check"] and has_garbled_text(text):
            issues.append("encoding_error")
        if issues:
            results["failed"] += 1
            results["issues"].append({"chunk_index": i, "issues": issues})
        else:
            results["passed"] += 1
    return results
```

## 解析器调用封装

### Docling (PDF学术论文)

```python
def parse_with_docling(file_path, **kwargs):
    """使用Docling解析PDF，返回统一格式chunks"""
    from docling.document_converter import DocumentConverter
    converter = DocumentConverter()
    result = converter.convert(file_path)
    chunks = []
    for item in result.document.export_to_dict().get("main-text", []):
        text = item.get("text", "")
        if text.strip():
            chunks.append({
                "text": text,
                "source": file_path,
                "parser": "docling",
                "metadata": {
                    "heading": item.get("heading"),
                    "page": item.get("prov", [{}])[0].get("page_no"),
                    "type": item.get("type", "text"),
                }
            })
    return chunks
```

### Marker (PDF→Markdown)

```python
def parse_with_marker(file_path, **kwargs):
    """使用Marker将PDF转为Markdown，再按heading分chunk"""
    from marker.converters.pdf import PdfConverter
    from marker.models import create_model_dict
    from marker.output import text_from_rendered
    model_dict = create_model_dict()
    converter = PdfConverter(artifact_dict=model_dict)
    rendered = converter(file_path)
    text, _, images = text_from_rendered(rendered)
    chunks = markdown_to_chunks(text, source=file_path, parser="marker")
    return chunks
```

### Crawl4AI (Web静态页面)

```python
async def parse_with_crawl4ai(url, **kwargs):
    """使用Crawl4AI爬取网页并提取结构化内容"""
    from crawl4ai import AsyncWebCrawler
    from crawl4ai.content_scraping_strategy import WebScrappingStrategy
    async with AsyncWebCrawler() as crawler:
        result = await crawler.arun(
            url=url,
            scraping_strategy=WebScrappingStrategy(),
            word_count_threshold=10,
        )
        chunks = [{
            "text": result.markdown,
            "source": url,
            "parser": "crawl4ai",
            "metadata": {"title": result.metadata.get("title")},
        }]
        return chunks
```

### Firecrawl (Web SPA/批量)

```python
def parse_with_firecrawl(url, mode="scrape", **kwargs):
    """使用Firecrawl爬取网页（支持SPA渲染和批量爬取）"""
    from firecrawl import FirecrawlApp
    app = FirecrawlApp()  # 自动从环境变量读取API key
    if mode == "crawl":
        result = app.crawl_url(url, params={"limit": 100})
        return [{"text": d.get("markdown", ""), "source": d.get("metadata", {}).get("sourceURL", url),
                 "parser": "firecrawl", "metadata": d.get("metadata", {})} for d in result.get("data", [])]
    else:
        result = app.scrape_url(url, params={"formats": ["markdown"]})
        return [{"text": result.get("markdown", ""), "source": url, "parser": "firecrawl",
                 "metadata": result.get("metadata", {})}]
```

### Zerox (OCR扫描件)

```python
async def parse_with_zerox(file_path, **kwargs):
    """使用Zerox对扫描件/图片PDF做OCR"""
    from py_zerox import zerox
    result = await zerox(file_path=file_path, model="gpt-4o-mini")
    return [{"text": page.content, "source": file_path, "parser": "zerox",
             "metadata": {"page": page.page_num}} for page in result.pages]
```

### Unstructured (通用ETL)

```python
def parse_with_unstructured(file_path, **kwargs):
    """使用Unstructured做通用文档解析"""
    from unstructured.partition.auto import partition
    elements = partition(filename=file_path)
    return [{"text": str(elem), "source": file_path, "parser": "unstructured",
             "metadata": {"type": elem.category}} for elem in elements]
```

## 输出适配

```python
def adapt_output(chunks, target, **kwargs):
    """将统一chunk格式转换为目标平台格式"""
    if target == "langchain":
        from langchain.schema import Document
        return [Document(page_content=c["text"], metadata=c.get("metadata", {})) for c in chunks]
    elif target == "llama-index":
        from llama_index.core import TextNode
        return [TextNode(text=c["text"], metadata=c.get("metadata", {})) for c in chunks]
    elif target == "chroma":
        return [{"id": f"chunk_{i}", "document": c["text"], "metadata": c.get("metadata", {})} 
                for i, c in enumerate(chunks)]
    elif target == "markdown":
        return "\n\n---\n\n".join(c["text"] for c in chunks)
    elif target == "json":
        import json
        return json.dumps(chunks, ensure_ascii=False, indent=2)
    else:
        return chunks
```

## 冲突检测（多源场景）

```python
def detect_conflicts(source_chunks):
    """检测多源数据之间的冲突"""
    conflicts = []
    seen_texts = {}
    for source, chunks in source_chunks.items():
        for chunk in chunks:
            text_key = chunk["text"][:200]
            if text_key in seen_texts:
                conflicts.append({
                    "type": "duplicate_content",
                    "sources": [seen_texts[text_key]["source"], source],
                    "severity": "low",
                    "suggestion": "deduplicate",
                })
            else:
                seen_texts[text_key] = {"source": source}
    return conflicts
```

## 完整编排流程

```python
class RAGDataOrchestrator:
    """RAG数据预处理编排器——数据清洗总入口"""
    
    def __init__(self, config=None):
        self.config = config or {}
        self.available_parsers = detect_available_parsers()
        self.quality_rules = {**QUALITY_RULES, **self.config.get("quality", {})}
    
    def process(self, source, source_type=None, parser=None, output="json"):
        """单源处理：检测→选择解析器→解析→质量断言→输出适配"""
        if not source_type:
            source_type = self._detect_source_type(source)
        if not parser:
            available = [p for p, info in self.available_parsers.items() 
                        if info["installed"] and info["env_ready"]]
            parser = select_parser(source_type, available=available)
        chunks = self._parse(source, parser)
        quality = assert_quality(chunks, self.quality_rules)
        adapted = adapt_output(chunks, output)
        return {"chunks": adapted, "quality_report": quality, "parser_used": parser,
                "source_type": source_type, "chunk_count": len(chunks)}
    
    def pipeline(self, config_path):
        """多源编排：按配置文件处理多个源，合并结果"""
        import yaml
        with open(config_path) as f:
            pipeline_config = yaml.safe_load(f)
        all_results = {}
        source_chunks = {}
        for source in pipeline_config["sources"]:
            result = self.process(source=source["path"], source_type=source.get("type"),
                                  parser=source.get("parser"))
            all_results[source["path"]] = result
            source_chunks[source["path"]] = result["chunks"]
        conflicts = detect_conflicts(source_chunks) if pipeline_config.get("quality", {}).get("conflict_detection") else []
        merged = self._merge(source_chunks, pipeline_config.get("quality", {}))
        output_format = pipeline_config.get("output", {}).get("format", "json")
        adapted = adapt_output(merged, output_format)
        return {"results": all_results, "conflicts": conflicts, "merged": adapted, "total_chunks": len(merged)}
    
    def _detect_source_type(self, source):
        from pathlib import Path
        if source.startswith(("http://", "https://")):
            return "web_static"
        if source.endswith(".pdf"):
            return "pdf_academic"
        if source.endswith((".docx", ".pptx", ".xlsx")):
            return "office"
        if Path(source).is_dir():
            return "code" if (Path(source) / ".git").exists() else "local"
        return "unknown"
    
    def _parse(self, source, parser):
        dispatch = {
            "docling": lambda: parse_with_docling(source),
            "marker": lambda: parse_with_marker(source),
            "crawl4ai": lambda: parse_with_crawl4ai(source),
            "firecrawl": lambda: parse_with_firecrawl(source),
            "zerox": lambda: parse_with_zerox(source),
            "unstructured": lambda: parse_with_unstructured(source),
        }
        if parser not in dispatch:
            raise ValueError(f"Unknown parser: {parser}")
        result = dispatch[parser]()
        import asyncio
        if asyncio.iscoroutine(result):
            result = asyncio.run(result)
        return result
    
    def _merge(self, source_chunks, quality_config):
        merged = []
        seen = set()
        for source, chunks in source_chunks.items():
            for chunk in chunks:
                text = chunk.get("text", chunk.get("content", ""))
                fp = text[:200]
                if quality_config.get("deduplicate") and fp in seen:
                    continue
                seen.add(fp)
                merged.append(chunk)
        return merged
```

## 与Skill Seekers的关系

| 维度 | Skill Seekers | RAG Data Orchestrator |
|------|--------------|----------------------|
| 定位 | 全能工具（自己实现所有解析器） | 编排层（调度最优解析器） |
| 解析质量 | 每种格式中等水平 | 每种格式用专业工具=最高水平 |
| 扩展方式 | 改核心代码 | 写插件适配器 |
| 适用场景 | 快速出活、不想装多个工具 | 追求质量、愿意配置最优工具链 |
| 可组合 | 可作为orchestrator的一个parser插件 | — |

**Skill Seekers可以作为orchestrator的一个parser插件使用**，尤其在代码仓库AST解析和冲突检测方面有独特价值。

## 常见问题

### Q: 为什么不直接用Skill Seekers？
A: Skill Seekers是垂直整合路线——自己实现18种解析器，每种都不如专业工具。比如PDF解析不如Docling，Web爬取不如Firecrawl。Orchestrator调度专业工具，每种格式都用领域最优解。

### Q: 为什么不直接用Unstructured？
A: Unstructured是最接近"总入口"的，但只输出JSON，没有多平台适配、没有质量断言层、没有解析器选择策略。Orchestrator把Unstructured作为通用fallback，但在专业场景调度更优工具。

### Q: 为什么不用LangChain的loaders？
A: LangChain loaders只管"加载"，不管"预处理质量"。没有质量断言、没有冲突检测、没有解析器选择。Orchestrator在loaders上游加了一层质量保障。

### Q: 解析器都没装怎么办？
A: 运行`rag-orchestrator doctor`查看缺失项，按提示安装。最少装一个Unstructured即可处理大部分格式，装齐6个覆盖所有场景。

## Pitfalls

1. **Docling首次运行会下载模型**（约1GB），需要网络和磁盘空间
2. **Marker依赖PyTorch**，GPU环境效果更好，CPU可用但慢
3. **Firecrawl需要API key**，免费额度有限（500页/月）
4. **Zerox调用GPT-4V**，扫描件OCR会产生API费用
5. **Crawl4AI的async API**需要在async环境中运行，同步调用需asyncio.run()
6. **Unstructured的all-docs安装很重**（约2GB），按需安装子集如pdf,docx
7. **多源合并时去重策略**：前200字符指纹可能误判，长文档建议用simhash
8. **质量断言的阈值**需要根据场景调整——学术论文chunk可以更长，聊天记录chunk应该更短
