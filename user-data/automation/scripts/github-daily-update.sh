#!/bin/bash
# GitHub Memory Daily Update Script
# Usage: ./github-daily-update.sh [topic]
# Without args: updates all tracked repos
# With topic: updates only repos in that topic

set -e

MEMORY_DIR="${HERMES_HOME:-~/.hermes}/github-memory"
SCRIPT_DIR="$(dirname "$0")"
TODAY=$(date +%Y-%m-%d)
LOG_DIR="${HERMES_HOME:-~/.hermes}/logs"
LOG_FILE="$LOG_DIR/github-tracker.log"

mkdir -p "$LOG_DIR" "$MEMORY_DIR/_reports"

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

error() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] ERROR: $1" | tee -a "$LOG_FILE"
}

# Ensure jq is available
if ! command -v jq &> /dev/null; then
    error "jq is required but not installed"
    exit 1
fi

# Ensure gh is authenticated
if ! gh auth status &> /dev/null; then
    error "GitHub CLI is not authenticated"
    exit 1
fi

update_repo() {
    local repo_dir="$1"
    local owner_repo=$(jq -r '.full_name' "$repo_dir/metadata.json" 2>/dev/null)
    
    if [ -z "$owner_repo" ] || [ "$owner_repo" = "null" ]; then
        error "Invalid metadata.json in $repo_dir"
        return 1
    fi
    
    log "Updating: $owner_repo"
    
    # Fetch current metrics
    local metrics_file=$(mktemp)
    trap "rm -f $metrics_file" RETURN
    
    if ! gh repo view "$owner_repo" --json stargazersCount,forksCount,pushedAt,openIssuesCount,watchersCount > "$metrics_file" 2>/dev/null; then
        error "Failed to fetch metrics for $owner_repo"
        return 1
    fi
    
    local stars=$(jq '.stargazersCount' "$metrics_file")
    local forks=$(jq '.forksCount' "$metrics_file")
    local pushed_at=$(jq -r '.pushedAt' "$metrics_file")
    local open_issues=$(jq '.openIssuesCount' "$metrics_file")
    local watchers=$(jq '.watchersCount' "$metrics_file")
    
    # Update stars history
    local stars_history="$repo_dir/history/stars.json"
    if [ -f "$stars_history" ]; then
        jq --arg date "$TODAY" --argjson count "$stars" \
            'if (. | length) == 0 or .[-1].date != $date then . += [{date: $date, count: $count}] else . end' \
            "$stars_history" > "${stars_history}.tmp" && mv "${stars_history}.tmp" "$stars_history"
    fi
    
    # Update forks history
    local forks_history="$repo_dir/history/forks.json"
    if [ -f "$forks_history" ]; then
        jq --arg date "$TODAY" --argjson count "$forks" \
            'if (. | length) == 0 or .[-1].date != $date then . += [{date: $date, count: $count}] else . end' \
            "$forks_history" > "${forks_history}.tmp" && mv "${forks_history}.tmp" "$forks_history"
    fi
    
    # Update commit activity (commits in last 30 days)
    local commits_history="$repo_dir/history/commits.json"
    local since=$(date -d "30 days ago" +%Y-%m-%d)
    local commit_count=$(gh api "repos/${owner_repo}/commits?since=${since}&per_page=100" --paginate --slurp -q 'length' 2>/dev/null || echo "0")
    
    if [ -f "$commits_history" ]; then
        jq --arg date "$TODAY" --argjson count "$commit_count" \
            'if (. | length) == 0 or .[-1].date != $date then . += [{date: $date, count: $count}] else . end' \
            "$commits_history" > "${commits_history}.tmp" && mv "${commits_history}.tmp" "$commits_history"
    fi
    
    # Update metadata.json
    local metadata_file="$repo_dir/metadata.json"
    jq --arg updated "$TODAY" \
       --argjson stars "$stars" \
       --argjson forks "$forks" \
       --argjson issues "$open_issues" \
       --argjson watchers "$watchers" \
       --arg pushed_at "$pushed_at" \
       '.last_updated = $updated | .stars = $stars | .forks = $forks | .open_issues = $issues | .watchers = $watchers | .pushed_at = $pushed_at' \
       "$metadata_file" > "${metadata_file}.tmp" && mv "${metadata_file}.tmp" "$metadata_file"
    
    log "  ✓ Stars: $stars, Forks: $forks, Commits(30d): $commit_count"
}

# Parse arguments
TOPIC="$1"

log "=== GitHub Memory Daily Update Started ==="
log "Memory directory: $MEMORY_DIR"
log "Date: $TODAY"

# Find repos to update
if [ -n "$TOPIC" ]; then
    REPO_DIRS=$(find "$MEMORY_DIR/$TOPIC" -name "metadata.json" -exec dirname {} \; 2>/dev/null || echo "")
else
    REPO_DIRS=$(find "$MEMORY_DIR" -path "*/history/stars.json" -exec dirname {} \; 2>/dev/null | sort -u || echo "")
fi

if [ -z "$REPO_DIRS" ]; then
    log "No repositories to update"
    exit 0
fi

TOTAL=0
SUCCESS=0
FAILED=0

for repo_dir in $REPO_DIRS; do
    TOTAL=$((TOTAL + 1))
    if update_repo "$repo_dir"; then
        SUCCESS=$((SUCCESS + 1))
    else
        FAILED=$((FAILED + 1))
    fi
done

log "=== Update Complete ==="
log "Total: $TOTAL, Success: $SUCCESS, Failed: $FAILED"

# Generate summary report
REPORT_FILE="$MEMORY_DIR/_reports/update-$(date +%Y%m%d).md"
cat > "$REPORT_FILE" << EOF
# GitHub Memory Update Report

**Date**: $TODAY  
**Total Repositories**: $TOTAL  
**Successful**: $SUCCESS  
**Failed**: $FAILED  

## Updated Repositories

| Repository | Stars | Forks | Commits(30d) |
|------------|-------|-------|--------------|
EOF

for repo_dir in $REPO_DIRS; do
    owner_repo=$(jq -r '.full_name' "$repo_dir/metadata.json" 2>/dev/null || echo "N/A")
    stars=$(jq '.stars // 0' "$repo_dir/metadata.json" 2>/dev/null || echo "0")
    forks=$(jq '.forks // 0' "$repo_dir/metadata.json" 2>/dev/null || echo "0")
    commits=$(jq -r '.[-1].count // 0' "$repo_dir/history/commits.json" 2>/dev/null || echo "0")
    echo "| $owner_repo | $stars | $forks | $commits |" >> "$REPORT_FILE"
done

log "Report saved: $REPORT_FILE"

exit 0
