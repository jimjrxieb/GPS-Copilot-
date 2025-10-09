#!/bin/bash
# Start GP-Copilot Auto-Sync Daemon

cd /home/jimmie/linkops-industries/GP-copilot

echo "🚀 Starting GP-Copilot Auto-Sync Daemon..."
echo ""

# Install watchdog if not present
if ! python3 -c "import watchdog" 2>/dev/null; then
    echo "📦 Installing watchdog library..."
    pip install watchdog --quiet
fi

# Run daemon
python3 GP-DATA/auto_sync_daemon.py
