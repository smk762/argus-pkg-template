# CLAUDE.md — argus-pkg-template

Guidance for AI agents working in this repo. Human-facing usage lives in [README.md](README.md).

## What this is

A [Copier](https://copier.readthedocs.io) template that scaffolds new Python packages for the [Argus suite](https://github.com/smk762?tab=repositories&q=argus) with the suite's shared conventions (uv tooling, `hatch-vcs` versioning, ruff config, the `argus-ci` reusable CI workflow, PyPI+GHCR release). Existing repos pull updates with `copier update`, so **a change here propagates across the whole suite**.

## Must never happen

Each row names what enforces it. An **UNENFORCED** row is a known gap: when one bites, add a check, not more prose.

| Never | Enforced by |
|---|---|
| A render that fails, or whose package doesn't install, lint or pass its tests, with `has_cli` / `has_server` on or off | `render.yml` (a matrix over both flags) |
| A question with no `default` and no `when:` (it breaks non-interactive scaffolds and prompts on every `copier update`) | `scripts/check_template.py`, which allows only `project_name` and `description` to be asked |
| README's questions table out of step with `copier.yml` | `scripts/check_template.py` |
| Stock `{{ }}` / `{% %}` in a template file (copied through as literal text) | `scripts/check_template.py --rendered` |
| A seed CLAUDE.md without the argus-suite block, or linking the suite map on `main` | `scripts/check_template.py --rendered` |
| The release workflow made a call into argus-ci | PyPI refuses trusted publishing from a reusable workflow (its `job_workflow_ref` check) |
| A seed whose Branches text differs from the suite's shared rule | **UNENFORCED** |

## Layout

- `copier.yml` — questions + `_envops`. **Critical:** Jinja delimiters are remapped to `[[ ]]` / `[% %]` / `[# #]` so that GitHub Actions `${{ }}` and Docker `{{ }}` pass through workflow templates untouched. Use those delimiters, not the stock `{{ }}`.
- `template/` — the scaffold (`_subdirectory: template`). Every file is `*.jinja` and is rendered on `copier copy`. Filenames themselves template: `src/[[ package_name ]]/`.
- `README.md` — documents the questions table (CI checks it matches `copier.yml`).
- `scripts/check_template.py` — the template's own checks; `.github/workflows/render.yml` runs them with a render matrix.

## Working on the template

- **Test a render before committing.** A broken Jinja expression only surfaces at scaffold time. CI (`render.yml`) renders every flag combination, but a local render is faster:
  ```bash
  uvx copier copy --trust . /tmp/scaffold-test --data project_name=argus-x --data description="x" --defaults
  ```
  Try it with `has_cli` / `has_server` both on and off — those flags gate whole blocks (`[% if has_server %]…[% endif %]`).
- Conditional fields use `when:` in `copier.yml` (e.g. `cli_name` only when `has_cli`). Whitespace in `[% if %]` blocks is load-bearing in rendered output (pyproject/Dockerfile) — match the existing style.
- The **release** workflow is intentionally a top-level workflow, not a call into `argus-ci`: PyPI trusted publishing can't run inside a reusable workflow.
- When you add a new templated file, no registration is needed — Copier renders everything under `template/`. Just make sure it uses the remapped delimiters.

## Branches

`dev` is the default branch and the base for every PR. Cut feature branches from `origin/dev` and bring them up to date by merging `origin/dev`, never `main`. Never push work to `main` or open a PR against it, except the release PR from `dev`: `main` must never be ahead of `dev`, with one exception. A release fast-forwards `main` to a `dev` commit that passed CI (`git push origin origin/dev:main`), then tags it. If `main` is protected, the release is a reviewed PR from `dev` into `main`, and merging it leaves a merge commit on `main` alone. That merge commit is the one exception to the rule: it leaves `main` one commit ahead of `dev` with an identical tree. Leave it there and don't merge `main` back into `dev`. Anything else on `main` that `dev` lacks is a mistake (`git diff origin/dev origin/main` must be empty). Once `main` carries such a commit it can't be fast-forwarded, so later releases are PRs too.

## Gotchas

- Existing suite repos have recorded answers in their `.copier-answers.yml`; a new question with no sensible default will prompt on every `copier update`.
- Editing `template/CLAUDE.md.jinja` changes the CLAUDE.md that *future* repos get — it is the seed, not the suite's per-repo guides.
