# CLAUDE.md — argus-pkg-template

Guidance for AI agents working in this repo. Human-facing usage lives in [README.md](README.md).

## What this is

A [Copier](https://copier.readthedocs.io) template that scaffolds new Python packages for the [Argus suite](https://github.com/smk762?tab=repositories&q=argus) with the suite's shared conventions (uv tooling, `hatch-vcs` versioning, ruff config, the `argus-ci` reusable CI workflow, PyPI+GHCR release). Existing repos pull updates with `copier update`, so **a change here propagates across the whole suite**.

## Layout

- `copier.yml` — questions + `_envops`. **Critical:** Jinja delimiters are remapped to `[[ ]]` / `[% %]` / `[# #]` so that GitHub Actions `${{ }}` and Docker `{{ }}` pass through workflow templates untouched. Use those delimiters, not the stock `{{ }}`.
- `template/` — the scaffold (`_subdirectory: template`). Every file is `*.jinja` and is rendered on `copier copy`. Filenames themselves template: `src/[[ package_name ]]/`.
- `README.md` — documents the questions table; keep it in sync with `copier.yml`.

## Working on the template

- **Test a render before committing.** A broken Jinja expression only surfaces at scaffold time:
  ```bash
  uvx copier copy --trust . /tmp/scaffold-test --data project_name=argus-x --data description="x" --defaults
  ```
  Try it with `has_cli` / `has_server` both on and off — those flags gate whole blocks (`[% if has_server %]…[% endif %]`).
- Conditional fields use `when:` in `copier.yml` (e.g. `cli_name` only when `has_cli`). Whitespace in `[% if %]` blocks is load-bearing in rendered output (pyproject/Dockerfile) — match the existing style.
- The **release** workflow is intentionally a top-level workflow, not a call into `argus-ci`: PyPI trusted publishing can't run inside a reusable workflow.
- When you add a new templated file, no registration is needed — Copier renders everything under `template/`. Just make sure it uses the remapped delimiters.

## Branches

`dev` is the default branch and the base for every PR. Cut feature branches from `origin/dev` and bring them up to date by merging `origin/dev`, never `main`. Never open a PR against `main` or push work to it directly: `main` must never be ahead of `dev`. A release fast-forwards `main` to a `dev` commit that passed CI (`git push origin origin/dev:main`), then tags it. If `main` is protected and needs a PR, merge the release PR, then immediately merge `main` back into `dev` so the merge commit is not left on `main` alone.

## Gotchas

- Adding a question to `copier.yml` without a default breaks non-interactive scaffolds — give it a default or a `when:`.
- Existing suite repos have recorded answers in their `.copier-answers.yml`; a new question with no sensible default will prompt on every `copier update`.
- Editing `template/CLAUDE.md.jinja` changes the CLAUDE.md that *future* repos get — it is the seed, not the suite's per-repo guides.
