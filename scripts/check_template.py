#!/usr/bin/env python3
"""Checks the template itself. Every Argus package is scaffolded from it and pulls it with `copier update`.

  * Every question in copier.yml has a `default` or a `when:`. A question without one breaks
    non-interactive scaffolds and prompts on every `copier update` of an existing repo. Only the
    questions in ASKED_ON_PURPOSE may be asked.
  * README.md's questions table lists exactly the questions in copier.yml.
  * With --rendered DIR: no stock `{{ }}` that mentions a copier question, and no `{% %}` block, survives a render.
    The template's delimiters are `[[ ]]` / `[% %]`, so stock Jinja is copied through as literal text.
    Other `{{ }}` is left alone on purpose: GitHub's `${{ }}` and docker/metadata-action's
    `{{version}}` must pass through.
    The rendered CLAUDE.md keeps the argus-suite block (argus-ci's suite-check needs it) and links
    the suite map on `dev`, never on `main`.

Usage: check_template.py [--rendered DIR ...]   (needs PyYAML)
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
ASKED_ON_PURPOSE = {"project_name", "description"}


def questions(path: Path = ROOT / "copier.yml") -> dict[str, dict]:
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    # Copier's shorthand `name: value` makes the scalar the default. A bare `name:` has none.
    return {
        k: v if isinstance(v, dict) else {} if v is None else {"default": v}
        for k, v in data.items()
        if not k.startswith("_")
    }


def unanswerable(qs: dict[str, dict]) -> list[str]:
    return sorted(k for k, v in qs.items() if "default" not in v and "when" not in v and k not in ASKED_ON_PURPOSE)


def readme_questions(path: Path = ROOT / "README.md") -> set[str]:
    return set(re.findall(r"^\|\s*`([a-z_]+)`\s*\|", path.read_text(encoding="utf-8"), re.MULTILINE))


def _stray_pattern(names: set[str]) -> re.Pattern[str]:
    # A question anywhere inside the braces, so `{{ '[' ~ test_extras ~ ']' }}` and `{{ 1 if x else 0 }}` count.
    if not names:
        return re.compile(r"\{%")
    return re.compile(r"\{%|(?<!\$)\{\{[^{}]*?\b(" + "|".join(sorted(map(re.escape, names))) + r")\b")


def stray(rendered: Path, names: set[str] | None = None) -> list[str]:
    pattern = _stray_pattern(names if names is not None else set(questions()))
    out = []
    for p in sorted(rendered.rglob("*")):
        rel = p.relative_to(rendered)  # an ancestor of `rendered` named .git or .venv must not skip the render
        if not p.is_file() or ".git" in rel.parts or ".venv" in rel.parts:
            continue
        try:
            text = p.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            continue
        for n, line in enumerate(text.splitlines(), 1):
            if pattern.search(line):
                out.append(f"{rel}:{n}: {line.strip()}")
    return out


def seed(rendered: Path) -> list[str]:
    try:
        text = (rendered / "CLAUDE.md").read_text(encoding="utf-8")
    except OSError:
        return ["the render has no CLAUDE.md"]
    out = []
    if "<!-- argus-suite" not in text:
        out.append("the rendered CLAUDE.md lacks the argus-suite block")
    if "argus-cortex/blob/dev/SUITE.md" not in text:
        out.append("the rendered CLAUDE.md doesn't link the suite map on dev")
    if "argus-cortex/blob/main/SUITE.md" in text:
        out.append("the rendered CLAUDE.md links the suite map on main")
    return out


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--rendered", nargs="*", default=[], type=Path)
    a = ap.parse_args(argv)
    errors = []
    qs = questions()
    for k in unanswerable(qs):
        errors.append(f"copier.yml: question `{k}` has no default and no `when:`")
    documented = readme_questions()
    for k in sorted(qs.keys() - documented):
        errors.append(f"README.md: question `{k}` is missing from the questions table")
    for k in sorted(documented - qs.keys()):
        errors.append(f"README.md: the questions table lists `{k}`, which copier.yml doesn't ask")
    for d in a.rendered:
        errors += [f"stock Jinja delimiter survived the render: {s}" for s in stray(d)]
        errors += seed(d)
    for e in errors:
        print(f"::error::{e}")
    print(f"{len(errors)} problem(s)")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
