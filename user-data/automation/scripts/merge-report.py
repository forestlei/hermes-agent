#!/usr/bin/env python3
"""
merge-report.py — 将分主题分析的中间结果合并为最终报告

用法:
  python3 merge-report.py --type weekly --period 2026-W15
  python3 merge-report.py --type monthly --period 2026-03

输入: .draft/ 目录下的主题分析文件
  - {period}-papers.md    (论文分析)
  - {period}-projects.md  (项目分析)
  - {period}-news.md      (新闻分析)
  - {period}-trends.md    (趋势分析)
  - {period}-data.json    (聚合数据，用于概览统计)

输出: 最终报告文件
  - weekly/YYYY-WNN.md 或 monthly/YYYY-MM.md
"""

import json
import os
import sys
import argparse
from datetime import datetime
from pathlib import Path

DATA_DIR = os.path.expanduser("~/.hermes/ai-daily-report/shared")


def read_draft(draft_dir, period, suffix):
    """读取主题分析的中间文件"""
    fpath = os.path.join(draft_dir, f"{period}-{suffix}")
    if os.path.exists(fpath):
        with open(fpath, "r", encoding="utf-8") as f:
            return f.read().strip()
    return None


def build_weekly_report(period, draft_dir, output_dir):
    """合并周报"""
    # 读取聚合数据（用于概览）
    data_path = os.path.join(draft_dir, f"{period}-data.json")
    meta = {}
    summary = {}
    if os.path.exists(data_path):
        with open(data_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            meta = data.get("meta", {})
            summary = data.get("summary", {})
    
    # 读取各主题分析
    papers_md = read_draft(draft_dir, period, "papers.md")
    projects_md = read_draft(draft_dir, period, "projects.md")
    news_md = read_draft(draft_dir, period, "news.md")
    trends_md = read_draft(draft_dir, period, "trends.md")
    
    # 解析period为日期范围
    start = meta.get("start", "")
    end = meta.get("end", "")
    year = period.split("-W")[0] if "-W" in period else ""
    week_num = period.split("-W")[1] if "-W" in period else ""
    
    # 构建报告
    report_parts = []
    
    # 标题
    report_parts.append(f"# AI 周报 — {year}年第{int(week_num)}周 ({start[5:]} ~ {end[5:]})")
    report_parts.append("")
    report_parts.append(f"> 自动生成的 AI 领域周报 | 本周收集: {summary.get('total_papers', 0)} 篇论文, "
                       f"{summary.get('total_projects', 0)} 个项目, "
                       f"{summary.get('total_news', 0)} 条新闻 | "
                       f"高质量论文: {summary.get('high_quality_papers', 0)} 篇")
    report_parts.append("")
    
    # 概览
    report_parts.append("## 📊 本周概览")
    report_parts.append("")
    report_parts.append(f"- **重要论文**: {summary.get('total_papers', 0)} 篇 (高质量 ≥75: {summary.get('high_quality_papers', 0)} 篇)")
    report_parts.append(f"- **热门项目**: {summary.get('total_projects', 0)} 个 (Stars ≥500: {summary.get('hot_projects', 0)} 个)")
    report_parts.append(f"- **行业动态**: {summary.get('total_news', 0)} 条")
    report_parts.append(f"- **数据覆盖**: {meta.get('days_with_data', '?')}/{meta.get('days_total', '?')} 天有数据")
    report_parts.append("")
    
    # 各主题部分
    if trends_md:
        report_parts.append("## 🎯 本周主题")
        report_parts.append("")
        report_parts.append(trends_md)
        report_parts.append("")
    
    if papers_md:
        report_parts.append("## 🔬 本周重要论文")
        report_parts.append("")
        report_parts.append(papers_md)
        report_parts.append("")
    
    if projects_md:
        report_parts.append("## 🚀 本周热门项目")
        report_parts.append("")
        report_parts.append(projects_md)
        report_parts.append("")
    
    if news_md:
        report_parts.append("## 📰 本周行业大事件")
        report_parts.append("")
        report_parts.append(news_md)
        report_parts.append("")
    
    # 趋势总结（如果有独立的趋势分析）
    if trends_md:
        report_parts.append("## 📈 周度趋势分析")
        report_parts.append("")
        report_parts.append(trends_md)
        report_parts.append("")
    
    # 信息源质量（从data.json提取）
    if meta:
        report_parts.append("## 📊 数据质量报告")
        report_parts.append("")
        report_parts.append(f"- 数据覆盖天数: {meta.get('days_with_data', '?')}/{meta.get('days_total', '?')}")
        source_cov = data.get("source_coverage", {}) if os.path.exists(data_path) else {}
        if source_cov:
            report_parts.append("- 信息源活跃度:")
            for src, days in sorted(source_cov.items(), key=lambda x: -x[1]):
                report_parts.append(f"  - {src}: {days}天")
        report_parts.append("")
    
    # 页脚
    report_parts.append("---")
    report_parts.append(f"*报告由 AI Daily Report 自动生成 | 覆盖周期: {start[5:]} ~ {end[5:]}*")
    
    return "\n".join(report_parts)


def build_monthly_report(period, draft_dir, output_dir):
    """合并月报"""
    data_path = os.path.join(draft_dir, f"{period}-data.json")
    meta = {}
    summary = {}
    if os.path.exists(data_path):
        with open(data_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            meta = data.get("meta", {})
            summary = data.get("summary", {})
    
    papers_md = read_draft(draft_dir, period, "papers.md")
    projects_md = read_draft(draft_dir, period, "projects.md")
    news_md = read_draft(draft_dir, period, "news.md")
    trends_md = read_draft(draft_dir, period, "trends.md")
    
    year = period.split("-")[0]
    month = period.split("-")[1]
    
    report_parts = []
    
    report_parts.append(f"# AI 月报 — {year}年{int(month)}月")
    report_parts.append("")
    report_parts.append(f"> 自动生成的 AI 领域月报 | 本月收集: {summary.get('total_papers', 0)} 篇论文, "
                       f"{summary.get('total_projects', 0)} 个项目, "
                       f"{summary.get('total_news', 0)} 条新闻 | "
                       f"高质量论文: {summary.get('high_quality_papers', 0)} 篇")
    report_parts.append("")
    
    report_parts.append("## 📊 月度概览")
    report_parts.append("")
    report_parts.append(f"- **收录论文**: {summary.get('total_papers', 0)} 篇 (高质量 ≥75: {summary.get('high_quality_papers', 0)} 篇)")
    report_parts.append(f"- **热门项目**: {summary.get('total_projects', 0)} 个 (Stars ≥500: {summary.get('hot_projects', 0)} 个)")
    report_parts.append(f"- **行业事件**: {summary.get('total_news', 0)} 条")
    report_parts.append(f"- **数据覆盖**: {meta.get('days_with_data', '?')}/{meta.get('days_total', '?')} 天有数据")
    report_parts.append("")
    
    if trends_md:
        report_parts.append("## 🏆 月度主题与趋势")
        report_parts.append("")
        report_parts.append(trends_md)
        report_parts.append("")
    
    if papers_md:
        report_parts.append("## 🔬 月度重要论文")
        report_parts.append("")
        report_parts.append(papers_md)
        report_parts.append("")
    
    if projects_md:
        report_parts.append("## 🚀 月度热门项目")
        report_parts.append("")
        report_parts.append(projects_md)
        report_parts.append("")
    
    if news_md:
        report_parts.append("## 📰 月度行业大事件")
        report_parts.append("")
        report_parts.append(news_md)
        report_parts.append("")
    
    report_parts.append("---")
    report_parts.append(f"*报告由 AI Daily Report 自动生成 | 覆盖周期: {year}年{int(month)}月*")
    
    return "\n".join(report_parts)


def main():
    parser = argparse.ArgumentParser(description="Merge theme analyses into final report")
    parser.add_argument("--type", required=True, choices=["weekly", "monthly"])
    parser.add_argument("--period", required=True, help="e.g. 2026-W15 or 2026-03")
    args = parser.parse_args()
    
    draft_dir = os.path.join(DATA_DIR, "reports", args.type, ".draft")
    output_dir = os.path.join(DATA_DIR, "reports", args.type)
    
    if not os.path.isdir(draft_dir):
        print(f"❌ Draft directory not found: {draft_dir}")
        sys.exit(1)
    
    # 检查中间文件
    required = ["papers.md", "projects.md", "news.md"]
    missing = []
    for suffix in required:
        if not read_draft(draft_dir, args.period, suffix):
            missing.append(suffix)
    
    if missing:
        print(f"⚠️  Missing draft files: {', '.join(missing)}")
        print("   Will generate report with available sections only.")
    
    # 构建报告
    if args.type == "weekly":
        report = build_weekly_report(args.period, draft_dir, output_dir)
    else:
        report = build_monthly_report(args.period, draft_dir, output_dir)
    
    # 保存
    output_path = os.path.join(output_dir, f"{args.period}.md")
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(report)
    
    print(f"✅ Report merged and saved to: {output_path}")
    print(f"   Total length: {len(report)} chars, ~{len(report.splitlines())} lines")


if __name__ == "__main__":
    main()
