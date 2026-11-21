"""Every Python a workflow tests or installs on must satisfy the package's ``requires-python``.

A package with ``python_min: 3.12`` once inherited a hard-coded 3.11 release matrix and failed its first release.
"""

from __future__ import annotations

import json
import tomllib
from pathlib import Path

import pytest
import yaml
from packaging.specifiers import SpecifierSet

ROOT = Path(__file__).resolve().parent.parent
WORKFLOWS = sorted((ROOT / ".github" / "workflows").glob("*.yml"))


def _requires_python() -> SpecifierSet:
    project = tomllib.loads((ROOT / "pyproject.toml").read_text())["project"]
    return SpecifierSet(project["requires-python"])


def _python_versions(node: object) -> list[str]:
    """Every ``python-version`` (scalar or matrix list) and ``python-versions`` (JSON list string) value."""
    found: list[str] = []
    if isinstance(node, dict):
        for key, value in node.items():
            if key == "python-version":
                found += [str(v) for v in value] if isinstance(value, list) else [str(value)]
            elif key == "python-versions":
                found += [str(v) for v in (json.loads(value) if isinstance(value, str) else value)]
            else:
                found += _python_versions(value)
    elif isinstance(node, list):
        for item in node:
            found += _python_versions(item)
    return found


def test_workflows_found() -> None:
    assert WORKFLOWS, "no workflows found under .github/workflows"


@pytest.mark.parametrize("workflow", WORKFLOWS, ids=lambda p: p.name)
def test_workflow_pythons_satisfy_requires_python(workflow: Path) -> None:
    spec = _requires_python()
    versions = _python_versions(yaml.safe_load(workflow.read_text()))
    # Expressions such as ${{ matrix.python-version }} resolve to a value checked where it is defined.
    literal = [v for v in versions if "${{" not in v]
    bad = [v for v in literal if not spec.contains(v)]
    assert not bad, f"{workflow.name} uses Python {bad}, outside requires-python {spec}"


def test_ci_and_release_test_the_minimum_python() -> None:
    """argus-ci's default matrix is 3.11 + 3.12, so ci.yml must pass its own; release must match it."""
    minimum = str(_requires_python()).removeprefix(">=")
    for name in ("ci.yml", "release.yml"):
        versions = _python_versions(yaml.safe_load((ROOT / ".github" / "workflows" / name).read_text()))
        assert minimum in versions, f"{name} does not test Python {minimum}: {versions}"
