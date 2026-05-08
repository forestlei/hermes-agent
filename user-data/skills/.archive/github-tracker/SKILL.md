---
name: github-tracker
description: Track GitHub repository metrics over time. Monitor stars, forks, commits, generate heat scores, detect trends, and produce growth reports.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [GitHub, Tracker, Metrics, Heat Score, Trends]
    capabilities:
      - metric_tracking
      - heat_scoring
      - trend_detection
      - growth_analysis
      - update_reports
---

# GitHub Tracker

You track GitHub repositories over time, analyzing growth patterns and generating heat scores. Your job is to monitor tracked repositories and detect meaningful trends.

## Memory Structure Reference

Tracked repos stored in `~/.hermes/github-memory/[topic]/[owner]/[repo]/`

## Metrics Collection

### 1. Collect All Metrics for a Repository

```bash
# Fetch current metrics
gh repo view owner/repo --json stargazersCount,forksCount,pushedAt,openIssuesCount,watchersCount,defaultBranch

# Fetch recent commits (last 30 days)
gh api repos/owner/repo/commits?per_page=100 --paginate --slurp

# Fetch contributors count
gh api repos/owner/repo/contributors --paginate -q 'length'

# Fetch latest release info
gh api repos/owner/repo/releases/latest --json tagName,publishedAt,assets 2>/dev/null
```

### 2. Update History Files

```bash
TODAY=$(date +%Y-%m-%d)

# Update stars (append new data point if last entry is not today)
STARS=$(gh repo view owner/repo --json stargazersCount --jq '.stargazersCount')
jq --arg date "$TODAY" --argjson stars "$STARS" \
  'if (. | length) == 0 or .[-1].date != $date then . += [{date: $date, count: $stars}] else . end' \
  history/stars.json > tmp.json && mv tmp.json history/stars.json

# Update forks
FORKS=$(gh repo view owner/repo --json forksCount --jq '.forksCount')
jq --arg date "$TODAY" --argjson forks "$FORKS" \
  'if (. | length) == 0 or .[-1].date != $date then . += [{date: $date, count: $forks}] else . end' \
  history/forks.json > tmp.json && mv tmp.json history/forks.json

# Update commit activity (commits in last 30 days)
SINCE=$(date -d "30 days ago" +%Y-%m-%d)
COMMITS=$(gh api repos/owner/repo/commits?since=$SINCE&per_page=100 --paginate --slurp -q 'length')
jq --arg date "$TODAY" --argjson commits "$COMMITS" \
  'if (. | length) == 0 or .[-1].date != $date then . += [{date: $date, count: $commits}] else . end' \
  history/commits.json > tmp.json && mv tmp.json history/commits.json
```

### 3. Batch Update All Tracked Repos

```bash
# For each tracked repo, run update
for repo in $(find ~/.hermes/github-memory -name "metadata.json" -exec dirname {} \;); do
  owner_repo=$(jq -r '.full_name' "$repo/metadata.json")
  topic=$(echo "$repo" | sed 's|.*github-memory/||' | cut -d'/' -f1)
  echo "Updating: $owner_repo"
  
  # Update metrics
  gh repo view "$owner_repo" --json stargazersCount,forksCount,pushedAt,openIssuesCount > /tmp/gh_update_$$.json
  
  # Update history files (stars, forks, commits)
  TODAY=$(date +%Y-%m-%d)
  # ... (apply jq updates as shown above)
  
  # Update metadata.json last_updated
  jq '.last_updated = "'$TODAY'"' "$repo/metadata.json" > tmp.json && mv tmp.json "$repo/metadata.json"
done
```

## Heat Score Calculation

### Algorithm

```
Heat Score = (Star Velocity × 0.4) + (Fork Velocity × 0.25) + (Commit Frequency × 0.2) + (Issue Activity × 0.15)

Where:
- Star Velocity = (stars_now - stars_30d_ago) / 30 days
- Fork Velocity = (forks_now - forks_30d_ago) / 30 days  
- Commit Frequency = commits_in_last_30_days
- Issue Activity = (open_issues_now - open_issues_30d_ago) / 30_days (capped at ±5)
```

### Calculate Heat Score

```bash
# Read history files
STARS_NOW=$(jq -r '.stargazersCount' metadata.json)
STARS_30D=$(jq -r '.[] | select(.date >= (now | strftime("%Y-%m-%d") | sub("T.*"; "") | .[:-6]))' history/stars.json 2>/dev/null | head -1)

# Alternative: calculate from history
STARS_30D_AGO=$(jq -r '.[-2].count // 0' history/stars.json)
STARS_NOW=$(jq -r '.[-1].count' history/stars.json)

# Calculate velocity
STARS_VELOCITY=$(echo "scale=4; ($STARS_NOW - $STARS_30D_AGO) / 30" | bc)

# Similar for forks...
FORK_VELOCITY=$(echo "scale=4; ($FORKS_NOW - $FORKS_30D_AGO) / 30" | bc)

# Commit frequency (from last 30 days)
COMMITS=$(jq -r '.[-1].count // 0' history/commits.json)

# Issue activity
ISSUES_NOW=$(jq -r '.open_issues // 0' metadata.json)
ISSUES_30D=5  # Would need historical issue data

# Calculate heat score
HEAT=$(echo "scale=2; ($STARS_VELOCITY * 0.4 * 100) + ($FORK_VELOCITY * 0.25 * 100) + ($COMMITS * 0.2) + ($ISSUES_ACTIVITY * 0.15 * 10)" | bc)
```

### Heat Score Levels

| Score | Level | Description |
|-------|-------|-------------|
| 80-100 | 🔥 Very Hot | Explosive growth, trending hard |
| 60-79 | 📈 Hot | Strong growth |
| 40-59 | ↗️ Warming | Moderate growth |
| 20-39 | ➡️ Stable | No significant change |
| 0-19 | 📉 Cooling | Declining activity |

## Trend Detection

### Trend Types

```bash
# Detect trend from history
# Use Python or jq to analyze

# Stars trend (last 7 vs previous 7 data points)
python3 << 'EOF'
import json

def analyze_trend(history):
    if len(history) < 4:
        return "insufficient_data"
    
    recent = history[-7:] if len(history) >= 7 else history[-3:]
    older = history[-14:-7] if len(history) >= 14 else history[:-len(recent)]
    
    if not older:
        return "insufficient_data"
    
    avg_recent = sum(d['count'] for d in recent) / len(recent)
    avg_older = sum(d['count'] for d in older) / len(older)
    
    if avg_recent > avg_older * 1.1:
        return "📈 growing"
    elif avg_recent < avg_older * 0.9:
        return "📉 declining"
    else:
        return "➡️ stable"
EOF
```

### Growth Rate Calculation

```bash
# Calculate growth rate over period
python3 << 'EOF'
import json

def growth_rate(history, days=30):
    if len(history) < 2:
        return 0
    
    current = history[-1]['count']
    # Find entry closest to days ago
    target_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
    older = None
    for entry in reversed(history):
        if entry['date'] <= target_date:
            older = entry['count']
            break
    
    if older is None and len(history) > 1:
        older = history[0]['count']
    elif older is None:
        return 0
    
    return ((current - older) / older) * 100 if older > 0 else 0
EOF
```

## Reports

### 1. Single Repo Tracker Report

```bash
cat > analysis/latest.md << 'EOF'
# Repository Tracker Report: owner/repo

## Current Metrics (as of YYYY-MM-DD)
| Metric | Value | 30d Change |
|--------|-------|------------|
| ⭐ Stars | X | +Y (Z%) |
| 🍴 Forks | X | +Y (Z%) |
| 📝 Commits (30d) | X | - |
| 📌 Open Issues | X | - |

## Heat Score
**Score: XX/100** - 🔥 Very Hot / 📈 Hot / etc

Calculated: (Star Vel: X/day × 0.4) + (Fork Vel: X/day × 0.25) + (Commits: X × 0.2) + (Issues: X × 0.15)

## Trend Analysis
| Period | Star Trend | Fork Trend | Activity |
|--------|-----------|------------|----------|
| 7 days | 📈 +X | 📈 +X | High |
| 30 days | 📈 +X% | ➡️ 0% | Medium |
| 90 days | 📉 -X% | 📈 +X% | Low |

## Growth Chart
```mermaid
lineChart
    x-axis 日期
    y-axis Stars
    2024-01-01, 1000
    2024-01-15, 1050
    2024-02-01, 1200
```

## Notable Events
- YYYY-MM-DD: Version X.Y released
- YYYY-MM-DD: Starred 1000 milestone

## Next Update
Scheduled: YYYY-MM-DD
EOF
```

### 2. Topic Summary Report

```bash
cat > ~/.hermes/github-memory/[topic]/_report.md << 'EOF'
# Topic Report: [topic-name]

## Summary
- Tracked Repos: N
- Total Stars: X
- Average Heat: XX/100

## Heat Leaderboard
| Rank | Repo | Stars | Heat Score | Trend |
|------|------|-------|------------|-------|
| 1 | owner/repo-a | 10k | 🔥 85 | 📈 |
| 2 | owner/repo-b | 5k | 📈 62 | ↗️ |

## All Tracked Repos
<!-- table of all repos -->
EOF
```

### 3. Full Memory Report

```bash
cat > ~/.hermes/github-memory/_reports/full-report-$(date +%Y%m%d).md << 'EOF'
# GitHub Memory Full Report

Generated: YYYY-MM-DD HH:MM

## Overview
- Total Topics: N
- Total Repositories: N
- Repositories with 🔥 Heat: N
- Repositories with 📈 Growing trend: N

## Topic Breakdown

### topic-name
| Repo | Stars | Forks | Heat | Trend | Last Updated |
|------|-------|-------|------|-------|--------------|
| ... | ... | ... | ... | ... | ... |

## Alert: Rapid Growth
Projects with heat score > 70:
- owner/repo (🔥 89) - Stars +200 in 7 days!

## Alert: Declining
Projects with negative trend:
- owner/repo (📉 -15% stars in 30 days)
EOF
```

## Scheduled Updates

### Daily Update Script

```bash
#!/bin/bash
# ~/.hermes/scripts/github-daily-update.sh

MEMORY_DIR=~/.hermes/github-memory
TODAY=$(date +%Y-%m-%d)

echo "GitHub Memory Daily Update - $TODAY"

for repo_dir in $(find "$MEMORY_DIR" -name "metadata.json" -exec dirname {} \;); do
  owner_repo=$(jq -r '.full_name' "$repo_dir/metadata.json")
  echo "Updating: $owner_repo"
  
  # Fetch current metrics
  gh repo view "$owner_repo" --json stargazersCount,forksCount,pushedAt,openIssuesCount > /tmp/gh_metrics_$$.json
  
  STARS=$(jq '.stargazersCount' /tmp/gh_metrics_$$.json)
  FORKS=$(jq '.forksCount' /tmp/gh_metrics_$$.json)
  
  # Update stars history
  jq --arg date "$TODAY" --argjson stars "$STARS" \
    'if (. | length) == 0 or .[-1].date != $date then . += [{date: $date, count: $stars}] else . end' \
    "$repo_dir/history/stars.json" > /tmp/stars_$$.json && mv /tmp/stars_$$.json "$repo_dir/history/stars.json"
  
  # Update forks history
  jq --arg date "$TODAY" --argjson forks "$FORKS" \
    'if (. | length) == 0 or .[-1].date != $date then . += [{date: $date, count: $forks}] else . end' \
    "$repo_dir/history/forks.json" > /tmp/forks_$$.json && mv /tmp/forks_$$.json "$repo_dir/history/forks.json"
  
  # Update metadata
  jq --arg updated "$TODAY" \
     --argjson stars "$STARS" \
     --argjson forks "$FORKS" \
     '.last_updated = $updated | .stars = $stars | .forks = $forks' \
     "$repo_dir/metadata.json" > /tmp/meta_$$.json && mv /tmp/meta_$$.json "$repo_dir/metadata.json"
  
  echo "  Stars: $STARS, Forks: $FORKS"
done

echo "Update complete: $TODAY"
```

### Cron Setup

```bash
# Add to crontab (daily at 9 AM)
0 9 * * * /bin/bash ~/.hermes/scripts/github-daily-update.sh >> ~/.hermes/logs/github-tracker.log 2>&1

# Or use Hermes cron (if available)
```

## Quick Commands

```bash
# Check heat score for a repo
python3 << 'EOF'
import json, sys
sys.path.insert(0, '/root/.hermes/scripts')
# Calculate from history files
EOF

# Find repos with fastest star growth
find ~/.hermes/github-memory -name "stars.json" -exec python3 -c "
import json, sys
data = json.load(open(sys.argv[1]))
if len(data) >= 7:
    recent = data[-1]['count']
    older = data[-7]['count']
    growth = recent - older
    print(f'{sys.argv[1]}: {growth} stars in 7 days')
" {} \;

# Generate trend report
gh api repos/owner/repo/stats/commit-activity --jq '.[] | .total'
```

## Important Notes

- Run updates at most once per day (GitHub caches, no benefit from more frequent)
- Keep history files as JSON arrays with date + count
- Heat score is relative - compare within topics or use your own baselines
- Commit frequency is raw count, normalize by team size for accuracy
- Archive repos that are truly dead (>1 year no commits, declining stars)
- Export reports before making bulk changes
