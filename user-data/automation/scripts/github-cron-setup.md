# GitHub Memory Cron Setup

## Setup Daily Automatic Updates

### Option 1: System Cron

```bash
# Edit crontab
crontab -e

# Add this line (runs daily at 9 AM):
0 9 * * * /bin/bash /root/.hermes/scripts/github-daily-update.sh >> /root/.hermes/logs/github-tracker.log 2>&1
```

### Option 2: Hermes Gateway Cron (if available)

```bash
# Use the gateway's built-in scheduler
/hermes cron add github-daily "0 9 * * *" "~/.hermes/scripts/github-daily-update.sh"
```

### Option 3: Systemd Timer (Linux)

```bash
# Create systemd service
cat > ~/.config/systemd/user/github-tracker.service << EOF
[Unit]
Description=GitHub Memory Daily Update

[Service]
Type=oneshot
ExecStart=/bin/bash /root/.hermes/scripts/github-daily-update.sh
Environment=HERMES_HOME=/root/.hermes
```

```bash
# Create systemd timer
cat > ~/.config/systemd/user/github-tracker.timer << EOF
[Unit]
Description=GitHub Memory Daily Update Timer

[Timer]
OnCalendar=daily
Persistent=true

[Install]
WantedBy=timers.target
```

```bash
# Enable and start
systemctl --user enable github-tracker.timer
systemctl --user start github-tracker.timer
```

## Verify Setup

```bash
# Check cron is installed
crontab -l

# Test run the script manually
~/.hermes/scripts/github-daily-update.sh

# Check log
tail -f ~/.hermes/logs/github-tracker.log
```

## Update Frequency

| Frequency | When to Use |
|-----------|--------------|
| Daily | Most projects - normal tracking |
| Twice daily | Fast-moving projects (trending) |
| Weekly | Stable/mature projects |
| Manual only | Experimental/hobby tracking |

## Stopping Updates

```bash
# Remove cron job
crontab -e
# Delete the github-tracker line

# Or for systemd
systemctl --user stop github-tracker.timer
systemctl --user disable github-tracker.timer
```
