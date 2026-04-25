$python = Join-Path $PSScriptRoot ".venv\Scripts\python.exe"

if (Test-Path $python) {
  & $python -m src.scripts.commit @args
  exit $LASTEXITCODE
}

uv run python -m src.scripts.commit @args
