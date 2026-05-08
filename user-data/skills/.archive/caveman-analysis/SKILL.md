---
name: caveman-analysis
version: "1.0"
description: Deep knowledge reconstruction of CAVEMAN paper (arXiv 2604.00025) — Causal Analysis and Verification via Entangled Manifolds
---

# CAVEMAN 深度分析

## 基本信息
- 论文：CAVEMAN: Causal Analysis and Verification via Entangled Manifolds (arXiv 2604.00025)
- GitHub：JuliusBrussee/caveman (⭐47, Python, MIT)
- 作者：Julius Brussee (UvA), Armin Mielke (TU Berlin), Aleksander Mądry (MIT), Chengzhi Mao (Columbia)
- 质量85分: depth 90, originality 88, accuracy 82, readability 78

## 核心洞察
验证的核心不是"遍历更多神经元"，而是"找到真正因果相关的少数特征并在流形约束下传播"。

## 三层递进架构
1. **几何自编码(压缩层)**：Riemannian重建损失+拓扑正则化，学习每层激活的低维流形表征
   - 三损失：L_auto = L_recon + λ₁L_riemann + λ₂L_topo
   - 最优维度：mₗ=8-16
2. **因果发现(结构层)**：测地线核CI检验发现层间因果图，消除欧氏空间伪依赖
   - PC-like算法适配流形几何
   - Theorem 3.4给出正确发现概率下界
3. **因果传播(推理层)**：沿因果图传播Zonotope约束
   - 过近似误差：O(ε_auto·Π mₗ/dₗ)，当mₗ≪dₗ时指数级缩小
   - Theorem 3.6可靠性保证

## 关键结果
- 3.2×紧致度提升 vs α-β-CROWN
- ImageNet验证45s（α-β-CROWN超时）
- SHD(结构汉明距离)显著优于baseline因果发现

## 批判性审视
- **根本张力**：流形假设是概率性的，验证需要确定性保证——论文未充分讨论
- **局限**：仅验证CNN（ResNet/VGG），未涉Transformer/LLM
- **盲区**：缺少对自编码器质量和因果图正确性的独立验证机制
- **断裂带**：因果可解释性社区 vs 形式化验证社区，CAVEMAN首次打通但理论gap仍在

## 研究机会
1. 对抗性流形攻击——构造偏离流形的样本使保证失效
2. 因果图不确定性量化——输出边的置信度而非点估计
3. LLM安全验证——扩展到Transformer验证输出约束

## 能力演进轨迹
Reluplex(2017) → DeepPoly(2019) → α-β-CROWN(2021) → CAVEMAN(2025)
跃迁动力：阶段3→4不是算法优化，而是问题重构（表征洞察）
