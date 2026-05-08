#!/usr/bin/env python3
"""
aggregate-report-data.py — 聚合周报/月报所需的原始数据，输出为结构化中间文件

用法:
  python3 aggregate-report-data.py --type weekly [--week 2026-W15]
  python3 aggregate-report-data.py --type monthly [--month 2026-03]

输出:
  weekly/.draft/YYYY-WNN-data.json  或  monthly/.draft/YYYY-MM-data.json
  
  包含:
  {
    "meta": {"type": "weekly", "period": "2026-W15", "start": "2026-04-06", "end": "2026-04-12"},
    "papers": [...],      # 去重后的所有论文
    "projects": [...],    # 去重后的所有项目
    "news": [...],        # 去重后的所有新闻
    "feeds": [...],       # RSS博客文章
    "daily_stats": {...}, # 每日采集统计
    "source_coverage": {...} # 信息源覆盖情况
  }
"""

import json
import os
import sys
import argparse
from datetime import datetime, timedelta
from pathlib import Path
from collections import defaultdict

DATA_DIR = os.path.expanduser("~/.hermes/ai-daily-report/shared")
COLLECTIONS_DIR = os.path.join(DATA_DIR, "collections")


def get_week_range(year, week_num):
    """获取ISO周的起止日期"""
    # ISO周：周一为第一天
    jan4 = datetime(year, 1, 4)
    week1_start = jan4 - timedelta(days=jan4.weekday())
    week_start = week1_start + timedelta(weeks=week_num - 1)
    week_end = week_start + timedelta(days=6)
    return week_start.strftime("%Y-%m-%d"), week_end.strftime("%Y-%m-%d")


def get_month_range(year, month):
    """获取月份的起止日期"""
    start = datetime(year, month, 1)
    if month == 12:
        end = datetime(year + 1, 1, 1) - timedelta(days=1)
    else:
        end = datetime(year, month + 1, 1) - timedelta(days=1)
    return start.strftime("%Y-%m-%d"), end.strftime("%Y-%m-%d")


def load_collection(date_str):
    """加载某天的采集数据"""
    day_dir = os.path.join(COLLECTIONS_DIR, date_str)
    if not os.path.isdir(day_dir):
        return None
    
    data = {"date": date_str}
    for fname in os.listdir(day_dir):
        if fname.endswith(".json"):
            fpath = os.path.join(day_dir, fname)
            try:
                with open(fpath, "r", encoding="utf-8") as f:
                    key = fname.replace(".json", "")
                    data[key] = json.load(f)
            except (json.JSONDecodeError, IOError):
                pass
    return data


def dedup_papers(all_papers):
    """按arxiv_id去重（去掉vN后缀），保留评分最高的版本"""
    seen = {}
    for p in all_papers:
        aid = p.get("arxiv_id", p.get("id", ""))
        # 去掉版本号 v1, v2 等
        base_id = aid.split("v")[0] if aid else ""
        if not base_id:
            continue
        score = p.get("quality_score", p.get("score", 0))
        if base_id not in seen or score > seen[base_id].get("quality_score", seen[base_id].get("score", 0)):
            seen[base_id] = p
    return list(seen.values())


def dedup_projects(all_projects):
    """按full_name去重，保留stars最多的版本"""
    seen = {}
    for p in all_projects:
        name = p.get("full_name", p.get("name", ""))
        if not name:
            continue
        stars = p.get("stargazers_count", p.get("stars", 0))
        if name not in seen or stars > seen[name].get("stargazers_count", seen[name].get("stars", 0)):
            seen[name] = p
    return list(seen.values())


def dedup_news(all_news):
    """按标题去重"""
    seen = set()
    result = []
    for n in all_news:
        title = n.get("title", "")
        if title and title not in seen:
            seen.add(title)
            result.append(n)
    return result


def aggregate(start_date, end_date, report_type, period_label):
    """聚合指定日期范围内的所有数据"""
    start = datetime.strptime(start_date, "%Y-%m-%d")
    end = datetime.strptime(end_date, "%Y-%m-%d")
    
    all_papers = []
    all_projects = []
    all_news = []
    all_feeds = []
    daily_stats = {}
    source_coverage = defaultdict(int)
    days_with_data = 0
    days_total = (end - start).days + 1
    
    current = start
    while current <= end:
        date_str = current.strftime("%Y-%m-%d")
        data = load_collection(date_str)
        
        if data:
            days_with_data += 1
            papers = data.get("papers", [])
            github = data.get("github", [])
            news = data.get("news", [])
            feeds = data.get("feeds", [])
            hf_papers = data.get("hf_papers", [])
            
            all_papers.extend(papers)
            if hf_papers:
                all_papers.extend(hf_papers)
            all_projects.extend(github)
            all_news.extend(news)
            all_feeds.extend(feeds)
            
            daily_stats[date_str] = {
                "papers": len(papers) + len(hf_papers),
                "projects": len(github),
                "news": len(news),
                "feeds": len(feeds),
            }
            
            # 统计信息源覆盖
            for key in data.keys():
                if key != "date" and isinstance(data[key], list) and len(data[key]) > 0:
                    source_coverage[key] += 1
        else:
            daily_stats[date_str] = {"papers": 0, "projects": 0, "news": 0, "feeds": 0}
        
        current += timedelta(days=1)
    
    # 去重
    deduped_papers = dedup_papers(all_papers)
    deduped_projects = dedup_projects(all_projects)
    deduped_news = dedup_news(all_news)
    
    # 按评分排序
    deduped_papers.sort(key=lambda p: p.get("quality_score", p.get("score", 0)), reverse=True)
    deduped_projects.sort(key=lambda p: p.get("stargazers_count", p.get("stars", 0)), reverse=True)
    
    # 构建输出
    output = {
        "meta": {
            "type": report_type,
            "period": period_label,
            "start": start_date,
            "end": end_date,
            "generated_at": datetime.now().isoformat(),
            "days_with_data": days_with_data,
            "days_total": days_total,
        },
        "papers": deduped_papers,
        "projects": deduped_projects,
        "news": deduped_news,
        "feeds": all_feeds,
        "daily_stats": daily_stats,
        "source_coverage": dict(source_coverage),
        "summary": {
            "total_papers": len(deduped_papers),
            "high_quality_papers": len([p for p in deduped_papers if p.get("quality_score", p.get("score", 0)) >= 75]),
            "total_projects": len(deduped_projects),
            "hot_projects": len([p for p in deduped_projects if p.get("stargazers_count", p.get("stars", 0)) >= 500]),
            "total_news": len(deduped_news),
            "total_feeds": len(all_feeds),
        }
    }
    
    return output


def main():
    parser = argparse.ArgumentParser(description="Aggregate report data")
    parser.add_argument("--type", required=True, choices=["weekly", "monthly"])
    parser.add_argument("--week", help="ISO week e.g. 2026-W15")
    parser.add_argument("--month", help="Month e.g. 2026-03")
    args = parser.parse_args()
    
    if args.type == "weekly":
        if args.week:
            year, week_num = args.week.split("-W")
            year, week_num = int(year), int(week_num)
        else:
            today = datetime.now()
            # 上一周
            last_week = today - timedelta(weeks=1)
            year, week_num, _ = last_week.isocalendar()
        
        start_date, end_date = get_week_range(year, week_num)
        period_label = f"{year}-W{week_num:02d}"
        output_dir = os.path.join(DATA_DIR, "reports", "weekly", ".draft")
    else:
        if args.month:
            year, month = map(int, args.month.split("-"))
        else:
            today = datetime.now()
            if today.month == 1:
                year, month = today.year - 1, 12
            else:
                year, month = today.year, today.month - 1
        
        start_date, end_date = get_month_range(year, month)
        period_label = f"{year}-{month:02d}"
        output_dir = os.path.join(DATA_DIR, "reports", "monthly", ".draft")
    
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, f"{period_label}-data.json")
    
    print(f"📊 Aggregating {args.type} data: {start_date} ~ {end_date}")
    
    result = aggregate(start_date, end_date, args.type, period_label)
    
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    
    print(f"✅ Data aggregated: {result['summary']['total_papers']} papers, "
          f"{result['summary']['total_projects']} projects, "
          f"{result['summary']['total_news']} news")
    print(f"   High-quality papers (≥75): {result['summary']['high_quality_papers']}")
    print(f"   Days with data: {result['meta']['days_with_data']}/{result['meta']['days_total']}")
    print(f"   Saved to: {output_path}")
    
    # 同时输出各主题的数据文件（供子任务使用）
    papers_path = os.path.join(output_dir, f"{period_label}-papers.json")
    projects_path = os.path.join(output_dir, f"{period_label}-projects.json")
    news_path = os.path.join(output_dir, f"{period_label}-news.json")
    
    with open(papers_path, "w", encoding="utf-8") as f:
        json.dump(result["papers"], f, ensure_ascii=False, indent=2)
    with open(projects_path, "w", encoding="utf-8") as f:
        json.dump(result["projects"], f, ensure_ascii=False, indent=2)
    with open(news_path, "w", encoding="utf-8") as f:
        json.dump({"news": result["news"], "feeds": result["feeds"], "daily_stats": result["daily_stats"]}, f, ensure_ascii=False, indent=2)
    
    print(f"   Theme files: {papers_path}, {projects_path}, {news_path}")


if __name__ == "__main__":
    main()
