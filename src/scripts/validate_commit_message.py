from __future__ import annotations

import re
import sys
from pathlib import Path

ALLOWED_TYPES = [
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
]

HEADER_PATTERN = re.compile(r"^(?P<type>\w+)(?:\((?P<scope>[^)]+)\))?(?P<breaking>!)?: (?P<subject>.+)$")
SCOPE_PATTERN = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
IGNORED_HEADER_PATTERNS = [
    re.compile(r"^Merge "),
    re.compile(r'^Revert "'),
    re.compile(r"^fixup! "),
    re.compile(r"^squash! "),
]


def read_commit_header(commit_msg_path: Path) -> str:
    content = commit_msg_path.read_text(encoding="utf-8", errors="replace")
    for line in content.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        return stripped
    return ""


def should_ignore(header: str) -> bool:
    return any(pattern.match(header) for pattern in IGNORED_HEADER_PATTERNS)


def validate_header(header: str) -> list[str]:
    errors: list[str] = []

    if len(header) > 100:
        errors.append("header deve ter no maximo 100 caracteres")

    match = HEADER_PATTERN.match(header)
    if not match:
        errors.append("formato invalido; use `<type>(<scope>): <subject>` ou `<type>: <subject>`")
        return errors

    commit_type = match.group("type") or ""
    scope = match.group("scope") or ""
    subject = match.group("subject") or ""

    if not commit_type:
        errors.append("type nao pode ser vazio")
    elif commit_type not in ALLOWED_TYPES:
        errors.append(f"type invalido `{commit_type}`; use um de: {', '.join(ALLOWED_TYPES)}")

    if scope and not SCOPE_PATTERN.fullmatch(scope):
        errors.append("scope deve estar em kebab-case")

    if not subject.strip():
        errors.append("subject nao pode ser vazio")
    elif subject.endswith("."):
        errors.append("subject nao pode terminar com ponto final")

    return errors


def main() -> int:
    if len(sys.argv) != 2:
        print("Uso: validate_commit_message.py <commit-msg-file>", file=sys.stderr)
        return 2

    commit_msg_path = Path(sys.argv[1]).resolve()
    if not commit_msg_path.exists():
        print(f"Arquivo de mensagem de commit nao encontrado: {commit_msg_path}", file=sys.stderr)
        return 2

    header = read_commit_header(commit_msg_path)
    if not header:
        print("Mensagem de commit vazia.", file=sys.stderr)
        return 1

    if should_ignore(header):
        return 0

    errors = validate_header(header)
    if not errors:
        return 0

    print("Mensagem de commit invalida:", file=sys.stderr)
    for error in errors:
        print(f"- {error}", file=sys.stderr)

    print("\nExemplos validos:", file=sys.stderr)
    print("- feat(api): add structured MT5 error responses", file=sys.stderr)
    print("- fix(ui): prevent pywebview callback crash", file=sys.stderr)
    print("- chore(repo): normalize line endings", file=sys.stderr)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
