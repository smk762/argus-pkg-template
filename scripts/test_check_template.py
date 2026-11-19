"""Unit tests for the template checks (stdlib unittest)."""
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import check_template as ct  # noqa: E402


class Checks(unittest.TestCase):
    def test_a_question_needs_a_default_or_when(self):
        qs = {"project_name": {}, "a": {"default": "x"}, "b": {"when": "[[ x ]]"}, "c": {"type": "str"}}
        self.assertEqual(ct.unanswerable(qs), ["c"])

    def test_shorthand_questions_become_dicts_that_keep_their_default(self):
        with tempfile.TemporaryDirectory() as d:
            f = Path(d) / "copier.yml"
            f.write_text("_min: 1\na: my-pkg\nb: false\nc: 0\nd: [x, y]\ne:\nf:\n  type: str\n")
            qs = ct.questions(f)
        self.assertEqual(qs, {"a": {"default": "my-pkg"}, "b": {"default": False}, "c": {"default": 0},
                              "d": {"default": ["x", "y"]}, "e": {}, "f": {"type": "str"}})
        self.assertEqual(ct.unanswerable(qs), ["e", "f"])

    def test_stray_looks_inside_a_render_that_sits_under_a_git_or_venv_directory(self):
        with tempfile.TemporaryDirectory() as d:
            for ancestor in (".git", ".venv"):
                rendered = Path(d) / ancestor / "out"
                (rendered / ".git").mkdir(parents=True)
                (rendered / ".venv").mkdir()
                (rendered / "README.md").write_text("# {{ project_name }}\n")
                (rendered / ".git" / "x").write_text("{{ project_name }}\n")
                (rendered / ".venv" / "x").write_text("{{ project_name }}\n")
                self.assertEqual(ct.stray(rendered, {"project_name"}), ["README.md:1: # {{ project_name }}"])

    def test_stray_stock_delimiters_are_found_but_actions_and_docker_patterns_are_not(self):
        with tempfile.TemporaryDirectory() as d:
            (Path(d) / "release.yml").write_text(
                "group: ci-${{ github.ref }}\ntype=semver,pattern={{major}}.{{minor}},value=${{ x }}\n")
            self.assertEqual(ct.stray(Path(d), {"project_name"}), [])
            (Path(d) / "README.md").write_text("# {{ project_name }}\n{% if x %}\n")
            self.assertEqual(len(ct.stray(Path(d), {"project_name"})), 2)

    def test_stray_finds_a_question_that_is_not_the_first_thing_in_the_braces(self):
        with tempfile.TemporaryDirectory() as d:
            (Path(d) / "Makefile").write_text(
                "a {{ '[' ~ test_extras ~ ']' }}\nb {{ 1 if has_cli else 0 }}\nc {{version}} ${{ has_cli }}\n")
            self.assertEqual(len(ct.stray(Path(d), {"test_extras", "has_cli", "version_build_arg"})), 2)
            self.assertEqual(ct.stray(Path(d), set()), [])

    def test_the_seed_keeps_the_suite_block_and_the_dev_link(self):
        with tempfile.TemporaryDirectory() as d:
            self.assertEqual(len(ct.seed(Path(d))), 1)
            (Path(d) / "CLAUDE.md").write_text("<!-- argus-suite -->\nhttps://github.com/x/argus-cortex/blob/main/SUITE.md\n")
            self.assertEqual(len(ct.seed(Path(d))), 2)
            (Path(d) / "CLAUDE.md").write_text(
                "<!-- argus-suite -->\nx/argus-cortex/blob/dev/SUITE.md\nx/argus-cortex/blob/main/SUITE.md\n")
            self.assertEqual(ct.seed(Path(d)), ["the rendered CLAUDE.md links the suite map on main"])

    def test_this_template_passes(self):
        self.assertEqual(ct.unanswerable(ct.questions()), [])
        self.assertEqual(ct.readme_questions(), set(ct.questions()))


if __name__ == "__main__":
    unittest.main()
