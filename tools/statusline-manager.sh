#!/bin/bash
# Enhanced Status Line Manager for Claude Code
# Provides comprehensive usage tracking with message counts, time limits, and costs

set -euo pipefail

# Configuration
CACHE_FILE="$HOME/.claude/statusline-cache"
CACHE_DURATION=10  # seconds
PYTHON_CMD="python"

# Ensure cache directory exists
mkdir -p "$HOME/.claude"

# Function to get enhanced status from our monitoring system
get_enhanced_status() {
    local python_script="
import asyncio
import sys
import os
sys.path.insert(0, os.path.join(os.getcwd(), 'src'))

try:
    from mcp_server_openai.monitoring.inline_display import get_statusline
    status = asyncio.run(get_statusline())
    print(status)
except Exception as e:
    # Fallback to ccusage if available
    import subprocess
    try:
        result = subprocess.run(['ccusage', 'daily', '--json'],
                              capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            import json
            data = json.loads(result.stdout)
            cost = data.get('total_cost', 0)
            tokens = data.get('total_tokens', 0)
            requests = data.get('total_requests', 0)
            print(f'🤖 Claude | 💰 \${cost:.3f} | 📨 {requests} msgs | 🧠 {tokens:,} tokens')
        else:
            print('🤖 Claude Code | 💰 Usage tracking active')
    except:
        print('🤖 Claude Code | 💰 Enhanced status available')
"

    if [[ -f "src/mcp_server_openai/monitoring/inline_display.py" ]]; then
        $PYTHON_CMD -c "$python_script" 2>/dev/null || echo "🤖 Claude Code | 💰 Enhanced monitoring"
    else
        # Fallback to basic ccusage
        ccusage statusline 2>/dev/null || echo "🤖 Claude Code | 💰 Ready"
    fi
}

# Function to check cache validity
is_cache_valid() {
    if [[ -f "$CACHE_FILE" ]]; then
        local cache_age=$(( $(date +%s) - $(stat -f %m "$CACHE_FILE" 2>/dev/null || stat -c %Y "$CACHE_FILE" 2>/dev/null || echo 0) ))
        [[ $cache_age -lt $CACHE_DURATION ]]
    else
        false
    fi
}

# Main logic
case "${1:-status}" in
    "status"|"")
        # Use cached result if valid
        if is_cache_valid; then
            cat "$CACHE_FILE"
        else
            # Generate new status and cache it
            status=$(get_enhanced_status)
            echo "$status" | tee "$CACHE_FILE"
        fi
        ;;
    "refresh")
        # Force refresh
        rm -f "$CACHE_FILE"
        get_enhanced_status | tee "$CACHE_FILE"
        ;;
    "test")
        # Test mode - show detailed info
        echo "=== Enhanced Status Line Test ==="
        echo "Cache file: $CACHE_FILE"
        echo "Cache valid: $(is_cache_valid && echo "Yes" || echo "No")"
        echo "Status: $(get_enhanced_status)"
        echo "================================="
        ;;
    *)
        echo "Usage: $0 [status|refresh|test]"
        exit 1
        ;;
esac
