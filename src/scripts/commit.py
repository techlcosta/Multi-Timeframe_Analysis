from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path

ALLOWED_TYPES = (
    "feat",
    "fix",
    "docs",
    "style",
    "refactor",
    "perf",
    "test",
    "build",
    "ci",
    "chore",
    "revert",
)
SCOPE_PATTERN = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
HEADER_MAX_LENGTH = 100


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Create a Conventional Commit message and run git commit."
    )
    parser.add_argument("type", choices=ALLOWED_TYPES, help="Commit type.")
    parser.add_argument("subject", nargs="+", help="Commit subject.")
    parser.add_argument(
        "--scope",
        help="Optional kebab-case scope, for example ui, api, or release-build.",
    )
    parser.add_argument(
        "--breaking",
        action="store_true",
        help="Mark the commit as a breaking change.",
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="Pass -a to git commit to include tracked file changes.",
    )
    parser.add_argument(
        "--no-verify",
        action="store_true",
        help="Pass --no-verify to git commit.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Only print the generated commit message.",
    )
    return parser.parse_args()


def build_header(args: argparse.Namespace) -> str:
    subject = " ".join(args.subject).strip()
    if not subject:
        raise ValueError("subject cannot be empty")
    if subject.endswith("."):
        raise ValueError("subject must not end with a period")

    scope = ""
    if args.scope:
        normalized_scope = args.scope.strip()
        if not SCOPE_PATTERN.fullmatch(normalized_scope):
            raise ValueError("scope must be kebab-case")
        scope = f"({normalized_scope})"

    breaking = "!" if args.breaking else ""
    header = f"{args.type}{scope}{breaking}: {subject}"
    if len(header) > HEADER_MAX_LENGTH:
        raise ValueError(
            f"header is too long ({len(header)} > {HEADER_MAX_LENGTH})"
        )

    return header


def run_commit(message: str, *, all_files: bool, no_verify: bool) -> int:
    cmd = ["git", "commit", "-m", message]
    if all_files:
        cmd.insert(2, "-a")
    if no_verify:
        cmd.append("--no-verify")

    completed = subprocess.run(cmd, check=False)
    return completed.returncode


def main() -> None:
    args = parse_args()

    try:
        header = build_header(args)
    except ValueError as exc:
        print(f"error: {exc}", file=sys.stderr)
        raise SystemExit(2) from exc

    if args.dry_run:
        print(header)
        return

    repo_root = Path(__file__).resolve().parents[2]
    print(f"commit message: {header}")
    print(f"repository: {repo_root}")
    raise SystemExit(
        run_commit(header, all_files=args.all, no_verify=args.no_verify)
    )


if __name__ == "__main__":
    main()
