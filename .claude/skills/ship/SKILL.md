---
name: ship
description: Commit, push, and create a PR for current changes
disable-model-invocation: true
allowed-tools: Bash(git *), Bash(gh pr create *), Bash(pre-commit *)
---

## Context

- Current branch: !`git branch --show-current`
- Git status: !`git status`
- Recent commits: !`git log --oneline -10`
- Uncommitted changes (staged + unstaged): !`git diff HEAD`
- Full branch diff vs main: !`git diff main...HEAD --stat`
- Branch commits: !`git log main..HEAD --oneline`

## Instructions

Ship the current branch: commit (if needed), push, and create a PR.
Do everything in as few messages as possible. Do not ask for confirmation.
Always run Bash commands with `dangerouslyDisableSandbox: true`.

### 1. Pre-commit checks

Run `pre-commit run --all-files`. If anything fails, fix it and re-run.

### 2. Branch

If on `main`, create a feature branch with a descriptive conventional name
(e.g. `feat/add-interpolation-tests`, `fix/player-health-overflow`).
Derive the name from the changes. If already on a feature branch, continue.

### 3. Commit

Skip this step if there are no uncommitted changes (clean working tree).

Otherwise, stage relevant files (prefer specific filenames over `git add -A`).
Never commit secrets (.env, credentials, tokens).

Commit message format — **conventional commits, 50/72 rule**:
- Title: max 50 chars, prefix with feat:, fix:, refactor:, chore:, etc.
- Blank line, then body wrapped at 72 chars if context is needed
- Plain text only, no markdown, no bullet points
- Focus on why, not what

Use a HEREDOC to pass the message to `git commit -m`.

### 4. Push

Push with `-u` to set upstream tracking.

### 5. Pull Request

Create a PR with `gh pr create` targeting `main`.

Use the full branch diff and commit history (not just uncommitted changes)
to understand what the PR covers.

PR format — keep it minimal:

```
## Summary
Brief description of what changed and why. 2-4 sentences max.
```

No test plan, no checklist. Return the PR URL when done.
