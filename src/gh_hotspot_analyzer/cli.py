from __future__ import annotations

import argparse
import json

from .analyzer import analyze_payload
from .github_client import FetchOptions, GitHubClient, load_payload, save_payload
from .report import render_report, save_report


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Analyze hot GitHub repositories and generate Markdown reports.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    fetch_parser = subparsers.add_parser("fetch", help="Fetch repository data from GitHub.")
    fetch_parser.add_argument("--days", type=int, default=30)
    fetch_parser.add_argument("--limit", type=int, default=30)
    fetch_parser.add_argument("--output", type=str, default=None)

    analyze_parser = subparsers.add_parser("analyze", help="Analyze a saved GitHub payload.")
    analyze_parser.add_argument("--input", type=str, required=True)

    report_parser = subparsers.add_parser("report", help="Generate a report from a saved GitHub payload.")
    report_parser.add_argument("--input", type=str, required=True)
    report_parser.add_argument("--output", type=str, default=None)

    run_parser = subparsers.add_parser("run", help="Fetch, analyze and report in one step.")
    run_parser.add_argument("--days", type=int, default=30)
    run_parser.add_argument("--limit", type=int, default=30)
    run_parser.add_argument("--input-save", type=str, default=None)
    run_parser.add_argument("--report-output", type=str, default=None)

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    if args.command == "fetch":
        client = GitHubClient()
        payload = client.fetch_hot_repositories(FetchOptions(days=args.days, limit=args.limit))
        path = save_payload(payload, args.output)
        print(f"Saved GitHub payload to: {path}")
        return

    if args.command == "analyze":
        payload = load_payload(args.input)
        analysis = analyze_payload(payload)
        print(json.dumps(analysis, ensure_ascii=False, indent=2))
        return

    if args.command == "report":
        payload = load_payload(args.input)
        analysis = analyze_payload(payload)
        report_content = render_report(analysis)
        path = save_report(report_content, args.output)
        print(f"Saved report to: {path}")
        return

    if args.command == "run":
        client = GitHubClient()
        payload = client.fetch_hot_repositories(FetchOptions(days=args.days, limit=args.limit))
        payload_path = save_payload(payload, args.input_save)
        analysis = analyze_payload(payload)
        report_content = render_report(analysis)
        report_path = save_report(report_content, args.report_output)
        print(f"Saved GitHub payload to: {payload_path}")
        print(f"Saved report to: {report_path}")
        return

    parser.error(f"Unknown command: {args.command}")


if __name__ == "__main__":
    main()
