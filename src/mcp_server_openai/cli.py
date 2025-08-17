import argparse

from .main import hello


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="mcp_server_openai", description="Project CLI")
    parser.add_argument("--name", default="world", help="Name to greet")
    return parser


def main() -> None:
    args = build_parser().parse_args()
    print(hello(args.name))


if __name__ == "__main__":
    main()
