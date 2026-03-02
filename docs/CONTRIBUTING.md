# Contributing Guide

This repository follows a **devel-first** branching strategy.

## Branch Naming

Use the following prefixes:

- `feat/*` for new features
- `fix/*` for bug fixes
- `chore/*` for maintenance and tooling

## Branch Flow

- Feature work: `feat/*` → Pull Request to `devel`
- Stabilization: `devel` → Pull Request to `main`
- Do **not** open feature PRs directly to `main`

## Exception: Hotfixes

Direct changes to `main` are only for urgent production hotfixes.

Recommended hotfix flow:

1. Create `hotfix/*` from `main`
2. Merge `hotfix/*` into `main`
3. Immediately sync `main` back into `devel`

## Required PR Checks

Every PR must pass:

- Tests: `pytest`
- Lint: `ruff check src/ tests/`
- Types: `mypy src/`
- At least one reviewer approval

## Required Sync-Back Rule (Manual)

After every `devel -> main` merge, the owner must manually sync `main` back into `devel` **within the same work window**.

This repository intentionally does not use an automated `main -> devel` sync workflow. The sync-back step is a mandatory human process and must be reviewer-verified.

```bash
git checkout devel
git fetch origin
git merge origin/main --no-ff -m "chore: sync main into devel"
git push origin devel
```

## Merge/Release Checklist

Before starting the next feature branch, confirm all items:

- [ ] `devel -> main` PR merged
- [ ] `main -> devel` sync completed
- [ ] Reviewer confirmed sync-back completion
- [ ] Branch protections and required checks are green

## Repository Settings (GitHub)

Set these in GitHub repository settings:

1. Default pull request base: `devel`
2. Branch protection on `devel` and `main`:
   - Require pull request before merge
   - Require status checks to pass
   - Include these required checks:
     - `CI Tests / tests`
     - `CI Lint / lint`
     - `CI Types / types`
