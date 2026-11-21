# argus-pkg-template

A [Copier](https://copier.readthedocs.io) template for new Python packages in the
[Argus suite](https://github.com/smk762?tab=repositories&q=argus). It bakes in the
suite's conventions so repos start consistent and stay that way via `copier update`.

What you get:

- `uv`-based tooling (`Makefile`, editable installs, `uv build`)
- `hatchling` + `hatch-vcs` — versions derived from git tags, no hand-edited version strings
- `ruff` lint/format config matching the rest of the suite
- **CI** wired to the shared [`argus-ci`](https://github.com/smk762/argus-ci) reusable workflow
- **Docs check** (`docs.yml` → argus-ci `docs-check.yml`): generated `docs/cli.md` must match the Typer CLI (`make docs` regenerates it), and published docs are scanned for private IPs, paths and emails
- **Release** to PyPI (OIDC trusted publishing) + GHCR on `v*` tags
  - kept as a *top-level* workflow because PyPI trusted publishing can't run inside a reusable workflow
- `src/` layout, `py.typed`, a smoke test, MIT license
- a starter `CLAUDE.md` — agent orientation seeded with the suite conventions, ready to flesh out

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
| `author`            | `smk762`                         | Author in pyproject and LICENSE.                    |
| `github_owner`      | `smk762`                         | GitHub owner used in links and the argus-ci workflow calls. |
| `brand_mark`        | `false`                          | README title is the package lockup from argus-cortex `brand/` (light/dark). Turn on once `brand/packages/<name>/` exists. |
| `python_min`        | `3.11`                           | Minimum Python; CI and release test it and the next minor. |
| `has_cli`           | `true`                           | Adds a Typer `cli` extra + console script.          |
| `cli_name`          | `project_name`                   | Console script name (asked only when `has_cli`).    |
| `has_server`        | `false`                          | Adds a FastAPI `server` extra + Docker `CMD`.       |
| `test_extras`       | `dev`                            | Extras installed for tests / CI.                    |
| `ruff_pin`          | `0.15.16`                        | Pin ruff (blank = latest).                          |
| `post_test`         | `""`                             | Optional CI command after pytest (e.g. a schema check). |
| `dockerfile`        | `Dockerfile`                     | Dockerfile used by the release image build.         |
| `image_name`        | `project_name`                   | GHCR image name.                                    |
| `version_build_arg` | `false`                          | Keep git out of the image entirely (see below); the release always passes `VERSION`. |

## How the image gets its version

The release builds the image with the tag as the `VERSION` build-arg, then runs
the loaded image, imports the package and compares its `__version__` to the tag
(as PEP 440 versions, so `v0.3.0-rc1` matches `0.3.0rc1`). Only a match is
pushed. The Dockerfile hands `VERSION` to hatch-vcs as
`SETUPTOOLS_SCM_PRETEND_VERSION` in the one shell that builds the package's
wheel, never as an `ENV`: that would persist in the image and also version any
dependency built from source. It must be the plain spelling — hatch-vcs passes
no dist name to setuptools-scm, so `SETUPTOOLS_SCM_PRETEND_VERSION_FOR_<DIST>`
is ignored.

`version_build_arg` only decides what a build *without* the build-arg does:

- **`false`** (default) — a local `docker build .` versions from git, so `.git`
  stays in the build context and the image installs the `git` binary, which
  `python:*-slim` does not ship.
- **`true`** — no git at all: `.dockerignore` excludes `.git`, the release job
  checks out at `fetch-depth: 1`, and a local build with no build-arg falls back
  to `0.0.0.dev0`.

Either way, `.dockerignore` must never list a path git tracks (`.github`,
`docs`, ...). Git inside the build sees it deleted and versions the image as a
dirty dev build (`X.Y.(Z+1).dev0+g<sha>.d<date>`). The generated
`tests/test_image_version.py` checks that, and that the build-arg stays wired.

## Python versions

`python_min` sets `requires-python`, the Docker base image, ruff's target, and
the versions CI and the release's `test-install` job run on: `python_min` and
the next minor. The generated `tests/test_workflows.py` fails if a workflow
names a Python outside `requires-python`.
