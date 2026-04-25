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

## Recommended Workflow

Use the standard Git flow directly:

```powershell
uv run python -m src.scripts.setup_git_hooks
git add .
git commit -m "fix(ui): prevent pywebview callback crash"
git push origin main
```

More examples:

```powershell
git commit -m "feat(api): add structured MT5 error responses"
git commit -m "docs(readme): improve project presentation"
git commit -m "ci(release): fix pnpm setup in GitHub Actions"
git commit -m "chore(repo): normalize line endings"
```

## Local Commit Template

To use the included commit template locally:

```powershell
git config commit.template .gitmessage.txt
```

To apply it globally on your machine:

```powershell
git config --global commit.template <absolute-path-to-your-template>
```

## Validation

Commit messages are validated locally by the repository `commit-msg` hook before the commit is created.

To enable the hook for your current clone:

```powershell
uv run python -m src.scripts.setup_git_hooks
```

The hook uses [src/scripts/validate_commit_message.py](./src/scripts/validate_commit_message.py) and blocks invalid commit messages immediately, instead of waiting for a GitHub workflow failure.
