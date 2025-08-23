# Token Usage Tracking and Cost Monitoring

This project now includes comprehensive token usage tracking and cost monitoring functionality with ccusage integration for precise Claude Code usage analysis.

## Features

### 🎯 Core Functionality
- **Real-time token usage tracking** via ccusage integration
- **Detailed cost analysis** with session and daily breakdowns
- **Cache efficiency monitoring** for optimized performance
- **Inline cost display** for status bars and CLI
- **Rate limiting** based on costs and token usage
- **Multi-format output** (compact, detailed, JSON)

### 📊 Token Breakdown
- Input tokens (prompt tokens)
- Output tokens (completion tokens)
- Cache creation tokens
- Cache read tokens
- Total effective tokens

### 💰 Cost Analysis
- Per-session costs
- Daily cost accumulation
- Hourly burn rate projections
- Per-request cost averages
- Budget limit warnings

## Usage

### CLI Commands

```bash
# Get compact statusline display
python -m mcp_server_openai.cli monitor statusline

# Get usage summary
python -m mcp_server_openai.cli monitor usage

# Get detailed statistics
python -m mcp_server_openai.cli monitor stats

# Get detailed statistics as JSON
python -m mcp_server_openai.cli monitor stats --json
```

### Claude Code Integration

#### Option 1: Using ccusage directly (Recommended)

Add this to your `~/.claude/settings.json` or `~/.config/claude/settings.json`:

```json
{
  "statusLine": {
    "type": "command",
    "command": "bunx ccusage statusline",
    "padding": 0
  }
}
```

#### Option 2: Using this project's monitoring

```json
{
  "statusLine": {
    "type": "command",
    "command": "python -m mcp_server_openai.cli monitor statusline",
    "padding": 0
  }
}
```

#### Option 3: Fallback command

```json
{
  "statusLine": {
    "type": "command",
    "command": "bunx ccusage statusline || python -m mcp_server_openai.cli monitor statusline || echo 'Claude | Usage unavailable'",
    "padding": 0
  }
}
```

### Sample Statusline Output

```
🤖 Claude-3.5-Sonnet | 💰 $0.035 session / $0.07 today | 🔥 $0.04/hr | 20% cache | 4h 55m left | 🧠 7,223
```

**Output breakdown:**
- `🤖 Claude-3.5-Sonnet` - Current model being used
- `💰 $0.035 session / $0.07 today` - Session cost / Daily total cost
- `🔥 $0.04/hr` - Current hourly burn rate
- `20% cache` - Cache hit efficiency percentage
- `4h 55m left` - Estimated time remaining (if available)
- `🧠 7,223` - Total tokens used

### Programmatic Usage

```python
from mcp_server_openai.monitoring import get_statusline, get_usage_summary

# Get statusline display
statusline = await get_statusline()
print(statusline)

# Get usage summary
summary = await get_usage_summary()
print(summary)

# Get detailed stats
from mcp_server_openai.monitoring import get_display_manager
manager = get_display_manager()
stats = await manager.get_detailed_summary()
```

## Configuration

### Environment Variables

```bash
# Enable/disable monitoring
export MCP_MONITORING_ENABLED=true

# ccusage integration settings
export MCP_CCUSAGE_ENABLED=true
export MCP_CCUSAGE_PREFER_BUNX=true
export MCP_CCUSAGE_TIMEOUT=10.0

# Cost limits
export MCP_COST_HOURLY_MAX=10.0
export MCP_COST_DAILY_MAX=100.0
export MCP_TOKENS_PER_HOUR_MAX=100000

# Display settings
export MCP_INLINE_DISPLAY_ENABLED=true
```

### YAML Configuration

Create a `monitoring.yaml` file:

```yaml
monitoring:
  enabled: true
  ccusage:
    enabled: true
    prefer_bunx: true
    timeout_seconds: 10.0
    statusline_format: "compact"
  cost_limits:
    hourly_max: 10.0
    daily_max: 100.0
    tokens_per_hour_max: 100000
    cache_efficiency_min: 0.1
  alerts:
    enabled: true
    warning_threshold: 0.8
    critical_threshold: 0.95
```

Set the config path:
```bash
export MCP_MONITORING_CONFIG_PATH=/path/to/monitoring.yaml
```

## ccusage Installation

### Quick (no installation)
```bash
bunx ccusage  # Using Bun (recommended)
npx ccusage@latest  # Using Node.js
```

### Global installation
```bash
npm install -g ccusage  # Requires Node.js
```

## Advanced Features

### Rate Limiting
The system includes cost-aware rate limiting to prevent runaway expenses:

```python
from mcp_server_openai.monitoring import CostAwareLimiter, CostLimits

# Configure limits
limits = CostLimits(
    hourly_max=10.0,
    daily_max=100.0,
    per_request_max=1.0,
    tokens_per_hour_max=100000
)

# Use with web frameworks
limiter = CostAwareLimiter(usage_tracker, limits)
await limiter.enforce_limits(request)
```

### ASGI Middleware
For web applications:

```python
from mcp_server_openai.monitoring import UsageMiddleware

app = Starlette()
app = UsageMiddleware(app, log_interval=300)  # Log every 5 minutes
```

### Custom Display Formats
Create custom status displays:

```python
from mcp_server_openai.monitoring import get_display_manager

manager = get_display_manager()
stats = await manager.get_current_usage()

# Custom format
custom_display = f"Model: {stats.model_name} | Cost: ${stats.session_cost:.3f} | Efficiency: {stats.tokens.cache_efficiency*100:.0f}%"
```

## Troubleshooting

### ccusage not found
If ccusage is not available, the system automatically falls back to:
1. claude-monitor (if available)
2. Mock data for development

### Unicode/Emoji Issues
On Windows terminals that don't support emojis, the CLI automatically falls back to text-only display.

### Rate Limiting
If you hit rate limits, check your configuration:
```bash
python -m mcp_server_openai.cli monitor stats --json | jq '.detailed_stats.burn_rate_per_hour'
```

## Integration Examples

### GitHub Actions
```yaml
- name: Check Claude Usage
  run: |
    python -m mcp_server_openai.cli monitor stats --json > usage.json
    echo "::notice::$(python -m mcp_server_openai.cli monitor usage)"
```

### Shell Aliases
```bash
alias claude-usage='python -m mcp_server_openai.cli monitor usage'
alias claude-status='python -m mcp_server_openai.cli monitor statusline'
alias claude-stats='python -m mcp_server_openai.cli monitor stats'
```

### Logging Integration
```python
import logging
from mcp_server_openai.monitoring import log_current_usage

# Log usage periodically
await log_current_usage()
```

This comprehensive monitoring system provides real-time visibility into your Claude API usage, helping you track costs, optimize performance, and stay within budget limits.
