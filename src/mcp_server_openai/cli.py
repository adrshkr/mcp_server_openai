import argparse
import asyncio

from .main import hello
from .monitoring.inline_display import get_display_manager, get_statusline, get_usage_summary


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="mcp_server_openai", description="Project CLI")

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Hello command
    hello_parser = subparsers.add_parser("hello", help="Say hello")
    hello_parser.add_argument("--name", default="world", help="Name to greet")

    # Monitoring commands
    monitor_parser = subparsers.add_parser("monitor", help="Usage monitoring commands")
    monitor_subparsers = monitor_parser.add_subparsers(dest="monitor_command", help="Monitor subcommands")

    # Statusline command for Claude Code integration
    monitor_subparsers.add_parser("statusline", help="Get compact statusline display")

    # Usage summary command
    monitor_subparsers.add_parser("usage", help="Get current usage summary")

    # Detailed stats command
    detailed_parser = monitor_subparsers.add_parser("stats", help="Get detailed usage statistics")
    detailed_parser.add_argument("--json", action="store_true", help="Output as JSON")

    return parser


async def run_monitor_command(args: argparse.Namespace) -> None:
    """Handle monitoring subcommands."""
    import sys

    # Ensure UTF-8 output for emojis
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    try:
        if args.monitor_command == "statusline":
            statusline = await get_statusline()
            print(statusline)
        elif args.monitor_command == "usage":
            usage = await get_usage_summary()
            print(usage)
        elif args.monitor_command == "stats":
            manager = get_display_manager()
            stats = await manager.get_detailed_summary()
            if args.json:
                import json

                print(json.dumps(stats, indent=2))
            else:
                print(f"Summary: {stats.get('summary', 'N/A')}")
                if "efficiency_metrics" in stats:
                    metrics = stats["efficiency_metrics"]
                    print(f"Tokens per dollar: {metrics.get('tokens_per_dollar', 0):.0f}")
                    print(f"Avg cost per request: ${metrics.get('avg_cost_per_request', 0):.4f}")
                    print(f"Cache efficiency: {stats.get('cache_efficiency', 'N/A')}")
        else:
            print("Unknown monitor command. Use --help for available options.")
    except UnicodeEncodeError:
        # Fallback for terminals that don't support emojis
        if args.monitor_command == "statusline":
            statusline = await get_statusline()
            # Replace emojis with text equivalents
            safe_statusline = (
                statusline.replace("🤖", "Claude").replace("💰", "$").replace("🔥", "Rate:").replace("🧠", "Tokens:")
            )
            print(safe_statusline)
        else:
            print("Error displaying output. Try using --json flag or check terminal encoding.")


def main() -> None:
    args = build_parser().parse_args()

    if args.command == "hello":
        print(hello(args.name))
    elif args.command == "monitor":
        asyncio.run(run_monitor_command(args))
    else:
        # Default behavior for backward compatibility
        if hasattr(args, "name"):
            print(hello(args.name))
        else:
            print("No command specified. Use --help for available options.")


if __name__ == "__main__":
    main()
