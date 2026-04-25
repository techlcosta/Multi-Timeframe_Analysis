"""Build script for FX Strategies (Windows-friendly, simple and reliable)."""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.config.config import VERSION as APP_VERSION

APP_NAME = "FXStrategies"
APP_DISPLAY_NAME = "FX Strategies"
APP_COMPANY_NAME = "FX Strategies"
APP_DESCRIPTION = "Desktop multi-timeframe trading dashboard powered by MetaTrader 5."
APP_COPYRIGHT = "Copyright (c) FX Strategies"

FRONTEND_DIR = PROJECT_ROOT / "frontend"
FRONTEND_DIST_DIR = FRONTEND_DIR / "dist"
SRC_MAIN_FILE = PROJECT_ROOT / "src" / "main.py"

PYINSTALLER_DIST_DIR = PROJECT_ROOT / "dist"
PYINSTALLER_WORK_DIR = PROJECT_ROOT / "build"
ENTRY_STUB = PROJECT_ROOT / "__pyinstaller_entry__.py"
VERSION_INFO_FILE = PROJECT_ROOT / "__pyinstaller_version_info.txt"


def run_command(cmd: list[str], cwd: Path | None = None) -> None:
    print("> " + " ".join(cmd))
    subprocess.run(cmd, cwd=str(cwd) if cwd else None, check=True, shell=False)


def resolve_cmd(*candidates: str) -> str | None:
    for candidate in candidates:
        resolved = shutil.which(candidate)
        if resolved:
            return resolved
    return None


def resolve_pnpm_cmd() -> list[str]:
    pnpm = resolve_cmd("pnpm.cmd", "pnpm.exe", "pnpm")
    if pnpm:
        return [pnpm]

    corepack = resolve_cmd("corepack.cmd", "corepack.exe", "corepack")
    if corepack:
        return [corepack, "pnpm"]

    raise FileNotFoundError(
        "pnpm/corepack nao encontrados no PATH. Para habilitar: `corepack enable pnpm`."
    )


def ensure_project_layout() -> None:
    if not FRONTEND_DIR.exists():
        raise FileNotFoundError(f"Diretorio frontend nao encontrado: {FRONTEND_DIR}")
    if not (FRONTEND_DIR / "package.json").exists():
        raise FileNotFoundError("Arquivo frontend/package.json nao encontrado.")
    if not SRC_MAIN_FILE.exists():
        raise FileNotFoundError("Arquivo src/main.py nao encontrado.")


def ensure_frontend_dependencies() -> None:
    node_modules_dir = FRONTEND_DIR / "node_modules"
    if node_modules_dir.exists():
        return

    pnpm_cmd = resolve_pnpm_cmd()
    print("\n[1/3] Instalando dependencias do frontend...")
    run_command([*pnpm_cmd, "install"], cwd=FRONTEND_DIR)


def build_frontend() -> None:
    pnpm_cmd = resolve_pnpm_cmd()
    print("\n[2/3] Build do frontend (Vite)...")
    run_command([*pnpm_cmd, "build"], cwd=FRONTEND_DIR)

    index_file = FRONTEND_DIST_DIR / "index.html"
    if not index_file.exists():
        raise FileNotFoundError(f"Build do frontend nao gerou: {index_file}")

    print(f"Frontend OK: {index_file}")


def write_entry_stub() -> None:
    content = """\
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

from src.main import main

if __name__ == "__main__":
    main()
"""
    ENTRY_STUB.write_text(content, encoding="utf-8")


def remove_entry_stub() -> None:
    if ENTRY_STUB.exists():
        ENTRY_STUB.unlink()


def normalize_windows_version(version: str) -> tuple[int, int, int, int]:
    raw_parts = [part.strip() for part in version.split(".")]
    numeric_parts = [int(part) for part in raw_parts if part.isdigit()]

    while len(numeric_parts) < 4:
        numeric_parts.append(0)

    major, minor, patch, build = numeric_parts[:4]
    return (major, minor, patch, build)


def write_version_info_file() -> None:
    version_tuple = normalize_windows_version(APP_VERSION)
    version_text = ".".join(str(part) for part in version_tuple)

    content = f"""\
VSVersionInfo(
  ffi=FixedFileInfo(
    filevers={version_tuple},
    prodvers={version_tuple},
    mask=0x3F,
    flags=0x0,
    OS=0x40004,
    fileType=0x1,
    subtype=0x0,
    date=(0, 0)
  ),
  kids=[
    StringFileInfo([
      StringTable(
        '040904B0',
        [
          StringStruct('CompanyName', '{APP_COMPANY_NAME}'),
          StringStruct('FileDescription', '{APP_DESCRIPTION}'),
          StringStruct('FileVersion', '{version_text}'),
          StringStruct('InternalName', '{APP_NAME}'),
          StringStruct('LegalCopyright', '{APP_COPYRIGHT}'),
          StringStruct('OriginalFilename', '{APP_NAME}.exe'),
          StringStruct('ProductName', '{APP_DISPLAY_NAME}'),
          StringStruct('ProductVersion', '{version_text}')
        ]
      )
    ]),
    VarFileInfo([VarStruct('Translation', [1033, 1200])])
  ]
)
"""
    VERSION_INFO_FILE.write_text(content, encoding="utf-8")


def remove_version_info_file() -> None:
    if VERSION_INFO_FILE.exists():
        VERSION_INFO_FILE.unlink()


def find_icon() -> Path | None:
    explicit_logo = PROJECT_ROOT / "src" / "assets" / "logo.ico"
    if explicit_logo.exists():
        return explicit_logo

    candidates = [
        PROJECT_ROOT / "src" / "assets" / "icon.ico",
        PROJECT_ROOT / "src" / "assets" / "app.ico",
        PROJECT_ROOT / "assets" / "icon.ico",
        PROJECT_ROOT / "assets" / "app.ico",
    ]
    for candidate in candidates:
        if candidate.exists():
            return candidate

    return None


def clean_pyinstaller_dirs() -> None:
    if PYINSTALLER_WORK_DIR.exists():
        shutil.rmtree(PYINSTALLER_WORK_DIR, ignore_errors=True)
    PYINSTALLER_WORK_DIR.mkdir(parents=True, exist_ok=True)
    PYINSTALLER_DIST_DIR.mkdir(parents=True, exist_ok=True)


def build_executable(onefile: bool) -> Path:
    print("\n[3/3] Gerando executavel (PyInstaller)...")
    clean_pyinstaller_dirs()
    write_entry_stub()
    write_version_info_file()

    data_separator = ";" if sys.platform.startswith("win") else ":"
    add_data = f"{FRONTEND_DIST_DIR}{data_separator}frontend/dist"

    cmd = [
        sys.executable,
        "-m",
        "PyInstaller",
        "--noconfirm",
        "--clean",
        "--name",
        APP_NAME,
        "--windowed",
        "--specpath",
        str(PYINSTALLER_WORK_DIR),
        "--distpath",
        str(PYINSTALLER_DIST_DIR),
        "--workpath",
        str(PYINSTALLER_WORK_DIR),
        "--version-file",
        str(VERSION_INFO_FILE),
        "--noupx",
        "--add-data",
        add_data,
        "--collect-all",
        "webview",
    ]

    if onefile:
        cmd.append("--onefile")
    else:
        cmd.append("--onedir")

    icon = find_icon()
    if icon is not None:
        cmd.extend(["--icon", str(icon)])
        print(f"Usando icone: {icon}")

    cmd.append(str(ENTRY_STUB))

    try:
        run_command(cmd, cwd=PROJECT_ROOT)
    finally:
        remove_entry_stub()
        remove_version_info_file()

    exe_path = (
        PYINSTALLER_DIST_DIR / f"{APP_NAME}.exe"
        if onefile
        else PYINSTALLER_DIST_DIR / APP_NAME / f"{APP_NAME}.exe"
    )
    if not exe_path.exists():
        raise FileNotFoundError(f"Executavel nao encontrado: {exe_path}")

    return exe_path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Build da aplicacao desktop (frontend + PyInstaller)"
    )
    parser.add_argument(
        "--onedir", action="store_true", help="Gera em modo onedir (padrao: onefile)"
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    onefile = not args.onedir

    try:
        ensure_project_layout()
        ensure_frontend_dependencies()
        build_frontend()
        exe_path = build_executable(onefile=onefile)
        print("\nBuild concluido com sucesso.")
        print(f"Executavel: {exe_path}")
    except subprocess.CalledProcessError as err:
        print(f"\nBuild falhou (comando): {err}")
        raise SystemExit(1) from err
    except Exception as err:
        print(f"\nBuild falhou: {err}")
        raise SystemExit(1) from err


if __name__ == "__main__":
    main()
