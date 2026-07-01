# argus-pkg-template

A [Copier](https://copier.readthedocs.io) template for new Python packages in the
[Argus suite](https://github.com/smk762?tab=repositories&q=argus). It bakes in the
suite's conventions so repos start consistent and stay that way via `copier update`.

What you get:

- `uv`-based tooling (`Makefile`, editable installs, `uv build`)
- `hatchling` + `hatch-vcs` — versions derived from git tags, no hand-edited version strings
- `ruff` lint/format config matching the rest of the suite
- **CI** wired to the shared [`argus-ci`](https://github.com/smk762/argus-ci) reusable workflow
- **Release** to PyPI (OIDC trusted publishing) + GHCR on `v*` tags
  - kept as a *top-level* workflow because PyPI trusted publishing can't run inside a reusable workflow
- `src/` layout, `py.typed`, a smoke test, MIT license

## Create a new package

```bash
uvx copier copy gh:smk762/argus-pkg-template ../argus-newthing
cd ../argus-newthing
git init && git add -A && git commit -m "Scaffold from argus-pkg-template"
gh repo create smk762/argus-newthing --public --source=. --push
```

## Update an existing package to the latest conventions

From inside a repo that was scaffolded from this template:

```bash
uvx copier update
```

Copier replays your recorded answers (`.copier-answers.yml`) and merges template
changes — handy for propagating CI/release/tooling updates across the suite.

## Questions

| Question            | Default                          | Purpose                                             |
| ------------------- | -------------------------------- | --------------------------------------------------- |
| `project_name`      | —                                | Distribution / pip name (e.g. `argus-widget`).      |
| `package_name`      | `project_name` with `-`→`_`      | Python import name.                                 |
| `description`       | —                                | One-liner for pyproject + README.                   |
| `python_min`        | `3.11`                           | Minimum Python.                                     |
| `has_cli`           | `true`                           | Adds a Typer `cli` extra + console script.          |
| `has_server`        | `false`                          | Adds a FastAPI `server` extra + Docker `CMD`.       |
| `test_extras`       | `dev`                            | Extras installed for tests / CI.                    |
| `ruff_pin`          | `0.15.16`                        | Pin ruff (blank = latest).                          |
| `post_test`         | `""`                             | Optional CI command after pytest (e.g. a schema check). |
| `dockerfile`        | `Dockerfile`                     | Dockerfile used by the release image build.         |
| `image_name`        | `project_name`                   | GHCR image name.                                    |
| `version_build_arg` | `false`                          | Pass `VERSION` build-arg (Dockerfiles that exclude `.git`). |
