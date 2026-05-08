---
name: enterprise-knowledge-platform
version: 0.1
description: 企业AI知识库平台架构方案 - GitHub版本控制+云存储+企业私有部署+技能共享
trigger: 企业知识库, 知识平台, 技能共享平台, enterprise knowledge base
---

# 企业AI知识库平台架构方案

## 用户核心需求
1. **版本控制** — 分支/PR/Review/Fork/回滚（类GitHub）
2. **云存储** — 文件同步/备份/分享/离线可用（类网盘）
3. **知识管理** — 结构化文档/标签/搜索/知识图谱（类Notion）
4. **技能共享** — 技能模板/评分/复用/个性化定制（技能市场）
5. **企业治理** — SSO/RBAC/审计/合规/私有部署
6. **AI增强** — 语义搜索/自动标签/智能推荐/知识问答

## 推荐架构：三层五组件

```
┌─────────────────────────────────────────────┐
│           统一入口层 (Gateway)                │
│      Nginx + Keycloak SSO + 统一搜索API      │
├──────────┬──────────┬───────────────────────┤
│ Forgejo  │Nextcloud │  Outline + AI中间件    │
│(版本控制) │(云存储)   │  (知识Wiki+智能增强)   │
├──────────┴──────────┴───────────────────────┤
│     PostgreSQL + Redis + MinIO(S3存储)       │
│     Docker Compose / K8s 部署                │
└─────────────────────────────────────────────┘
```

## 组件选型理由

| 组件 | 选型 | 理由 |
|------|------|------|
| 版本控制 | Forgejo (非Gitea) | 社区治理更开放，轻量Go实现，内置CI/CD，API兼容GitHub |
| 云存储 | Nextcloud | 开源最成熟，WebDAV协议，插件生态丰富，企业级权限 |
| 知识Wiki | Outline | Markdown原生，实时协作，Slack/飞书集成，自托管 |
| AI中间件 | 自研 | 语义搜索(embedding)+自动标签+知识问答(RAG) |
| SSO | Keycloak | 开源IAM标准，OIDC/SAML/LDAP全支持，RBAC细粒度 |
| 对象存储 | MinIO | S3兼容，轻量，可后续迁移云S3 |
| 搜索 | Meilisearch/ES | 全文+向量混合检索 |

## 状态
- 仅完成1/5概要部分，需继续：详细组件配置、部署方案、技能市场设计、数据流、安全方案
