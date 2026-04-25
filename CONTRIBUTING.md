# Contributing

## Commit Convention

This repository uses a Conventional Commits style.

Format:

```text
<type>(<scope>): <subject>
```

Scope is optional:

```text
<type>: <subject>
```

Examples:

```text
feat(api): add structured MT5 error responses
fix(ui): handle MT5 fetch failures without breaking pywebview
docs(readme): add multilingual project documentation
ci(release): build desktop app on version tags
chore(repo): normalize line endings with gitattributes
```

Allowed types:

- `feat`
- `fix`
- `docs`
- `style`
- `refactor`
- `perf`
- `test`
- `build`
- `ci`
- `chore`
- `revert`

Rules:

- Use lowercase for the commit type.
- Keep the optional scope in `kebab-case`.
- Write a short imperative subject.
- Do not end the subject with a period.
- Keep the header at or below 100 characters.

## Local Commit Template

To use the included commit template locally:

```powershell
git config commit.template .gitmessage.txt
```

To apply it globally on your machine:

```powershell
git config --global commit.template <absolute-path-to-your-template>
```

## Commit Helper

The repository also includes a small helper to generate a valid commit message and call `git commit` for you:

```powershell
uv run python -m src.scripts.commit fix --scope ui "prevent pywebview callback crash"
```

Useful examples:

```powershell
uv run python -m src.scripts.commit feat --scope api "add structured MT5 error responses"
uv run python -m src.scripts.commit docs --scope readme "improve project presentation"
uv run python -m src.scripts.commit ci --scope release "build Windows binary on version tags"
uv run python -m src.scripts.commit fix --scope ui "prevent pywebview callback crash" --dry-run
```

If you want an even shorter PowerShell command from the repository root:

```powershell
.\cc.ps1 fix --scope ui "prevent pywebview callback crash"
```

Options:

- `--scope <name>` adds an optional kebab-case scope
- `--breaking` generates `type(scope)!: subject`
- `--all` passes `-a` to `git commit`
- `--no-verify` forwards `--no-verify`
- `--dry-run` only prints the generated message

## Validation

GitHub Actions validates commit messages on pushes and pull requests using the rules from `commitlint.config.cjs`.
