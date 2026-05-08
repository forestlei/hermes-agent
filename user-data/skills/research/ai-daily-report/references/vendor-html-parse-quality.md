# 厂商HTML解析质量记录

## 问题概述

厂商官方更新页的HTML解析经常返回低价值内容，而非实质性新闻。预收集任务不会对cn_news条目评分（所有条目quality_score=0），因此报告生成时必须手动筛选。

## 各厂商解析质量详情（2026-05-05验证）

### DeepSeek官方 (api-docs.deepseek.com/updates)
- **返回内容**：版本历史条目，格式为 "Date: YYYY-MM-DD" + "DeepSeek-Vx.x"
- **示例**：`Date: 2026-04-24`, `DeepSeek-V4`, `Date: 2025-12-01`, `DeepSeek-V3.2`
- **问题**：无文章正文、无功能描述、无技术细节，仅版本号+日期
- **可用性**：⚠️ 仅版本号有用（可推断发布时间），需结合HuggingFace模型页获取详细信息
- **建议**：与HuggingFace(deepseek-ai)源交叉验证，后者有模型名称+描述

### Qwen官方 (qwenlm.github.io/blog + HF API)
- **返回内容**：模型更新名称，格式为 "Qwen/模型名"
- **示例**：`Qwen/SAE-Res-Qwen3.5-35B-A3B-Base-W128K-L0_100`, `Qwen/SAE-Res-Qwen3.5-27B-W80K-L0_100`
- **问题**：仅模型名+最后更新时间，无发布说明、无功能描述
- **可用性**：⚠️ 模型名可推断产品线（SAE-Res = 稀疏自编码器残差），但缺乏新闻价值
- **建议**：优先用HF API `https://huggingface.co/api/models?author=Qwen&sort=lastModified&direction=-1&limit=5` 获取结构化数据

### 智谱AI更新日志 (open.bigmodel.cn/dev/api/cn/update/new-releases)
- **返回内容**：Nextra/Next.js站点的导航页面
- **示例**：`Documentation Index`, `平台定位`, `平台优势`, `模型矩阵`, `开发套件`
- **问题**：解析到的是站点导航而非实际更新日志内容
- **可用性**：❌ 完全无价值，需改进解析逻辑或改用其他数据源
- **建议**：检查是否有API端点返回JSON格式的更新日志；或改用HuggingFace(internlm)源

### 百度千帆更新 (cloud.baidu.com/doc/WENXINWORKSHOP/s/Um1w9y59n)
- **返回内容**：通用平台页面
- **示例**：`百度千帆·大模型服务及Agent开发平台`, `学习路径`, `了解`, `费用说明`, `平台操作`
- **问题**：解析到的是文档导航而非更新记录
- **可用性**：❌ 完全无价值
- **建议**：需要找到实际的更新日志API端点，或改用其他百度信息源

## HuggingFace中文厂商过滤（替代方案）

当厂商HTML解析质量差时，HuggingFace模型更新是更可靠的信息源：

| 厂商 | HF组织 | 典型返回 | 质量 |
|------|--------|----------|------|
| DeepSeek | deepseek-ai | DeepSeek-V4-Flash, V4-Flash-Base, V4-Pro-Base | ✅ 有模型名+描述 |
| 零一万物 | 01-ai | Yi-34B-Chat, Yi-9B, Yi-6B-Chat | ⚠️ 老模型混入 |
| 百川 | baichuan-inc | Baichuan-M3-235B-GPTQ-INT4, Baichuan-M2-32B | ✅ 有量化版本信息 |
| MiniMax | MiniMaxAI | MiniMax-M2.7, MiniMax-M2.5, MiniMax-M2.1 | ✅ 版本演进清晰 |
| InternLM | internlm | CapRL-Eval-3B, CapRL-3B, CapRL-InternVL3.5-8B | ✅ 新产品线信息 |
| 阶跃星辰 | stepfun-ai | Step-3.5-Flash, Step-3.5-Flash-Base | ✅ 有变体信息 |
| 字节跳动 | ByteDance | Ouro-1.4B-Thinking, Ouro-2.6B-Thinking, Q-Insight | ✅ 新产品线信息 |

## 报告生成时的筛选策略

1. **厂商官方源**：仅保留有实质性内容的条目（新模型发布、重大功能更新），过滤掉导航/版本列表/通用页面
2. **HF厂商源**：优先使用，但需注意老模型混入问题（检查lastModified是否在近7天内）
3. **交叉验证**：同一厂商的更新应在多个源中出现（官方+HF+媒体报道），单源信息标注[~]
4. **评分替代**：由于quality_score=0，使用源权威性作为筛选依据：厂商官方(90+) > HF模型更新(85+) > 媒体报道(80+)
