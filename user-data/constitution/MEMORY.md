## ⚠️ 最顶层体系（不可遗忘）
- **顶层逻辑 = persistent-solver v3.2 的8条规则**
- 规则8（渐进性披露）下包含：十大主题分类 + 四种认知推理范式 + 十条核心建议
- 编码7条规则只是十大主题中"编码"主题的快速索引子集，不是顶层逻辑
- 定义文件：skills/software-development/persistent-solver/SKILL.md
§
## 十大主题分类（最顶层，所有任务归入其一）
1.编码(确定性) 2.知识(系统性+操作约束) 3.决策(概率性) 4.沟通(确定性) 5.管理(系统性) 6.分析(系统性) 7.创造(创造性) 8.探索(创造性) 9.验证(确定性) 10.优化(系统性)
- 知识主题操作约束（溯源追踪→交叉验证→结构化整理的展开）：来源优先级/引用约束/内部优先/确定性边界/冲突标注/小样本验证/更新约束(重写综合+追加证据)/归档约束(按查询意图)/噪声约束(宁缺毋滥)/衰减约束/写后索引/想法生命周期
- 约束来源：从GBrain知识管理实践中提炼，去除工具绑定，保留逻辑内核
§
## 四个永久话题（home base，永不衰减归档）
🧠知识体系(llm-wiki+fact-check+source-evolution) | 📰信息收集(RSS+头条+微信+cron) | 🔬AI前沿追踪(arxiv+GitHub+日报) | 🛠️技能体系(persistent-solver+新技能发现)
§
## 工作/研究主题（topics/，隶属永久话题下的项目级）
🔧work: agent-framework, news-insight, patent-intelligence, pptx-gen
📚research(归档): ai4science, ontology-special
⚠️ 主题有三个维度：永久话题(WHY)→工作主题(WHAT)→GitHub Memory(WITH WHAT)。用户问"主题"时可能指任一维度，必须全部展示或确认。
§
## 飞书chat_id
- ai日报群=oc_6ed1cc645057da3bbe93c6120219a61e, Home=oc_f489c8fb929b38e98888c932d900d4f6
- AI日报群：✅回答问题/发消息/推日报/重发日报 ❌改技能/执行命令/有副作用操作
§
## 技能Git同步（强制）
- 技能改后必执行：bash ~/.hermes/scripts/auto-sync-skills.sh
- 数据改后必执行：bash ~/.hermes/scripts/auto-sync-data.sh [commit_msg]
- RULES.md在skills仓库根目录，防记忆丢失
§
## 今日头条AI文章评估
- 80分达标线，4维度：accuracy/depth/originality/readability
- 红旗：声称开源但无GitHub链接/仓库404=虚假夸大(30%文章)
- 达标共性：架构级分析框架非功能列表堆砌；信噪比极低达标率~20%
- **生态归属造假**：文章把无关"撞名"项目归入知名生态。已验证案例：rusty_hermes(Meta JS引擎)被归入Hermes Agent生态、hermes-five(IoT平台)被归入Hermes Agent生态、hermes-go(独立AI框架碰巧叫hermes)被归入Hermes Agent生态。语言标注也常错：nullclaw标Rust实为Zig。处理：逐项目读README验证归属，扣accuracy -15，标记"生态归属造假"
- **Agent框架≠执行平台**：头条把"用底层语言重写Agent框架"等同于"执行平台"，但重写语言不增加沙箱/隔离/权限能力。用Zig重写OpenClaw还是OpenClaw，不会变成执行平台
§
## 项目/技能录入规则
- 每录入新项目或新技能，分析是否可用于已有主题(topics/)，若可用注册到skills/registry.json
§
## GitHub星标数量级误读模式
- 头条文章常见把"3.3万⭐"写成"33万⭐"的10倍虚标（万/千混淆）
- 已发现案例：GitNexus实际33,765⭐被写成33万，daily_stock_analysis实际33,456⭐被写成32.7万
- 处理方式：总是通过GitHub API验证，虚标扣accuracy -10~15，标记"星标数量级误读"
- 已写入toutiao-article-fetcher技能
§
项目选型评分方法论（用户纠正v3.3）：star数是核心要素，与技术实现同等重要。正确方法=两步法：①技术适配度门槛(≥20/55)排除非相关项目 ②Star(log归一化50%)+Tech(归一化50%)综合评分。不能纯技术排序（v3.2错误：281⭐排#1），也不能纯star排序（3478⭐UI框架不是执行平台）。
§
## GitHub Memory知识库
- 11个主题，155个条目（2026-05-08更新）
- 主题：智能体项目(45)|AI基础设施(22)|工具与资源(26)|AI应用平台(11)|pptx生成(12)|数据工程AI(10)|安全与隐私(10)|AI研究(5)|开发工具(6)|开源硬件(1)|本体与语义(8)
- 2026-05-08新增：onyx-dot-app/EnterpriseRAG-Bench(150⭐) → 工具与资源+AI基础设施
§
## 用户知识优先规则（anti-overruling）
- 用户直接经验 > API数据时间戳。当用户说"我5月2日确认过没有新版本"而GitHub API显示4月30日发布，不要坚持API数据
- GitHub published_at/created_at不一定等于"对用户可见"时间（draft→publish延迟、assets上传延迟）
- 遇到矛盾时诚实表述："API显示X但你确认Y，我无法确定哪方准确"，不要说"你错了"
- 此规则适用于：版本发布时间、功能可用性、部署状态等用户有直接经验的领域
§
## 日报/周报/月报GitHub项目录入规则
- 只有被**推荐/精选**上报告的GitHub项目需要录入github-memory（~/.hermes/github-memory/），不是所有出现的都录
- 范围：🚀GitHub趋势的top picks + 报告中有详细分析推荐的项目
- 录入流程：创建metadata.json → 更新_index.yaml → auto-sync-data.sh
- 去重：先检查metadata.json是否已存在
§
## 执行平台选型v4.0（2026-05-05完成）
- 4层架构：安全执行(沙箱)+编排调度+权限治理+经验共享(P0自研)
- 推荐技术栈：OpenSandbox(主力)+Firecracker(高安全)+WasmEdge(轻量)+agent-os(编排)+KubeArmor(权限)
- 三源交叉验证：GitHub搜索284+awesome-agent-sandboxes 26+已有数据，14个项目awesome独有
- 头条"高性能生态矩阵"全部不适合做执行平台（重写Agent框架≠执行平台）
- Daytona 72K⭐不推荐：AGPL-3.0+定位开发环境+重量级
§
## 知识编译跨专题（2026-05-07研究完成）
- 三层框架：L1经典(SDD/d-DNNF→本体推理加速) + L2 LLM(文档→结构化知识库) + L3技能(知识→可执行技能)
- 14个候选项目：L1有PySDD(73⭐)/rsdd(31⭐)/KCBox(27⭐)/cirkit(138⭐)/pyjuice(99⭐)/d-dnnf-reasoner(10⭐)；L2有WeKnora(14K⭐)/karpathy-llm-wiki(754⭐)/llm-wiki(367⭐)/synthadoc(236⭐)/athenaeum(9⭐)；L3有claude-memory-compiler(996⭐)/tensorlogic(39⭐)/Pluck.jl(15⭐)
- 跨专题归属：L1→本体与语义, L2→本体与语义+工具与资源, L3→智能体项目
- SkillRouter(arXiv:2603.22455)与L3直接相关：渐进披露=KC信息损失, body=完整电路, 假阴性过滤=等价性检测
- 参考文件：skills/research/github-research-assistant/references/knowledge-compilation-research-2026-05.md
- 实现状态：待用户确认后创建github-memory子专题
§
## L7人机交互层+Hermes桌面端（2026-05-05完成）
- 8项需求：H1多Agent|H2多平台|H3流式|H4任务可视化|H5权限可视化|H6技能管理|H7多模态|H8群组协作
- 推荐：open-webui(136K⭐主力)+hermes-web-ui(3.6K⭐Hermes原生)+CopilotKit(30K⭐SDK)+mission-control(4.6K⭐编排)
- hermes-web-ui：Vue3+Koa2, 8平台频道/SSE流式/技能浏览/群聊, Browser→BFF(:8648)→Gateway(:8642)
- 风险：AionUi License=NOASSERTION; hermes-web-ui仅1个月需观察