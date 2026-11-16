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

    def test_stray_stock_delimiters_are_found_but_actions_and_docker_patterns_are_not(self):
        with tempfile.TemporaryDirectory() as d:
            (Path(d) / "release.yml").write_text(
                "group: ci-${{ github.ref }}\ntype=semver,pattern={{major}}.{{minor}},value=${{ x }}\n")
            self.assertEqual(ct.stray(Path(d), {"project_name"}), [])
            (Path(d) / "README.md").write_text("# {{ project_name }}\n{% if x %}\n")
            self.assertEqual(len(ct.stray(Path(d), {"project_name"})), 2)

    def test_the_seed_keeps_the_suite_block_and_the_dev_link(self):
        with tempfile.TemporaryDirectory() as d:
            self.assertEqual(len(ct.seed(Path(d))), 1)
            (Path(d) / "CLAUDE.md").write_text("<!-- argus-suite -->\nhttps://github.com/x/argus-cortex/blob/main/SUITE.md\n")
            self.assertEqual(len(ct.seed(Path(d))), 1)

    def test_this_template_passes(self):
        self.assertEqual(ct.unanswerable(ct.questions()), [])
        self.assertEqual(ct.readme_questions(), set(ct.questions()))


if __name__ == "__main__":
    unittest.main()
