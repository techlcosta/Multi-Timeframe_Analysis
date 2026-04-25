from __future__ import annotations

import subprocess
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
HOOKS_DIR = PROJECT_ROOT / ".githooks"
HOOKS_PATH_VALUE = ".githooks"


def main() -> None:
    if not HOOKS_DIR.exists():
        raise FileNotFoundError(f"Diretorio de hooks nao encontrado: {HOOKS_DIR}")

    subprocess.run(
        ["git", "config", "core.hooksPath", HOOKS_PATH_VALUE],
        cwd=PROJECT_ROOT,
        check=True,
        shell=False,
    )
    print(f"Hooks Git configurados com sucesso: {HOOKS_DIR}")


if __name__ == "__main__":
    main()
