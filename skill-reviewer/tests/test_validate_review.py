"""
skill-reviewer 自校验脚本单元测试
运行方式：python -m unittest tests.test_validate_review -v
"""

import sys
import json
import tempfile
import subprocess
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
SCRIPT = REPO / "scripts" / "validate_review.py"

def _run(args: list[str]) -> subprocess.CompletedProcess:
    cmd = [sys.executable, str(SCRIPT)] + args
    return subprocess.run(cmd, capture_output=True, text=True, cwd=str(REPO))


class TestSpecMode(unittest.TestCase):
    def test_spec_pass(self):
        r = _run(["--spec", str(REPO)])
        self.assertEqual(r.returncode, 0, f"Spec should PASS: {r.stderr}")
        self.assertIn("[SPEC]", r.stdout)

    def test_name_uppercase(self):
        with tempfile.TemporaryDirectory() as td:
            td = Path(td)
            (td / "SKILL.md").write_text("---\nname: My-Skill\ndescription: test\n---\n")
            r = _run(["--spec", str(td)])
            self.assertEqual(r.returncode, 1)
            self.assertIn("大写字符", r.stderr)

    def test_name_leading_hyphen(self):
        with tempfile.TemporaryDirectory() as td:
            td = Path(td)
            (td / "SKILL.md").write_text("---\nname: -bad\ndescription: test\n---\n")
            r = _run(["--spec", str(td)])
            self.assertEqual(r.returncode, 1)
            self.assertIn("连字符开头", r.stderr)

    def test_name_double_hyphen(self):
        with tempfile.TemporaryDirectory() as td:
            td = Path(td)
            (td / "SKILL.md").write_text("---\nname: bad--name\ndescription: test\n---\n")
            r = _run(["--spec", str(td)])
            self.assertEqual(r.returncode, 1)
            self.assertIn("连续连字符", r.stderr)

    def test_name_too_long(self):
        with tempfile.TemporaryDirectory() as td:
            td = Path(td)
            long_name = "a" * 65
            (td / "SKILL.md").write_text(f"---\nname: {long_name}\ndescription: test\n---\n")
            r = _run(["--spec", str(td)])
            self.assertEqual(r.returncode, 1)
            self.assertIn("64 字符上限", r.stderr)

    def test_description_empty(self):
        with tempfile.TemporaryDirectory() as td:
            td = Path(td)
            dir_name = td.name
            (td / "SKILL.md").write_text(f"---\nname: {dir_name}\ndescription: '  '\n---\n")
            r = _run(["--spec", str(td)])
            self.assertEqual(r.returncode, 1)
            self.assertIn("为空", r.stderr)

    def test_description_too_long(self):
        with tempfile.TemporaryDirectory() as td:
            td = Path(td)
            long_desc = "x" * 1025
            (td / "SKILL.md").write_text(f"---\nname: test\ndescription: {long_desc}\n---\n")
            r = _run(["--spec", str(td)])
            self.assertEqual(r.returncode, 1)
            self.assertIn("1024 字符上限", r.stderr)


class TestExitCodes(unittest.TestCase):
    def test_fail_returns_1(self):
        with tempfile.TemporaryDirectory() as td:
            td = Path(td)
            (td / "SKILL.md").write_text("no frontmatter")
            r = _run(["--spec", str(td)])
            self.assertEqual(r.returncode, 1)

    def test_pass_returns_0(self):
        r = _run(["--spec", str(REPO)])
        self.assertEqual(r.returncode, 0)

    def test_bad_path_returns_2(self):
        r = _run(["--spec", "/nonexistent/path"])
        self.assertEqual(r.returncode, 2)


class TestJsonOutput(unittest.TestCase):
    def test_json_pass(self):
        r = _run(["--spec", str(REPO), "--json"])
        self.assertEqual(r.returncode, 0)
        data = json.loads(r.stdout)
        self.assertEqual(data["status"], "PASS")
        self.assertIn("modes", data)
        self.assertIn("spec", data["modes"])

    def test_json_total_not_truncated(self):
        with tempfile.TemporaryDirectory() as td:
            td = Path(td)
            (td / "SKILL.md").write_text("no frontmatter at all")
            r = _run(["--spec", str(td), "--json", "--output", "1"])
            data = json.loads(r.stdout)
            spec_result = data["modes"]["spec"]
            self.assertGreaterEqual(spec_result["total"], len(spec_result["errors"]))


class TestConsistencyMode(unittest.TestCase):
    def test_consistency_pass(self):
        r = _run(["--consistency", str(REPO)])
        self.assertEqual(r.returncode, 0, f"Consistency should PASS: {r.stderr}")

    def test_abbrev_detection(self):
        with tempfile.TemporaryDirectory() as td:
            td = Path(td)
            (td / "SKILL.md").write_text("---\nname: test\ndescription: test\n---\n\nP-V-E is old term.\n")
            r = _run(["--consistency", str(td)])
            self.assertEqual(r.returncode, 1)
            self.assertIn("PVE-ABBREV", r.stderr)

    def test_arrow_detection(self):
        with tempfile.TemporaryDirectory() as td:
            td = Path(td)
            arrow = "\u2192"
            content = f"---\nname: test\ndescription: test\n---\n\nPlan {arrow} Validate {arrow} Execute is old.\n"
            (td / "SKILL.md").write_text(content, encoding="utf-8")
            r = _run(["--consistency", str(td)])
            self.assertEqual(r.returncode, 1)
            self.assertIn("PVE-ARROW", r.stderr)

    def test_w4_old_detection(self):
        with tempfile.TemporaryDirectory() as td:
            td = Path(td)
            (td / "SKILL.md").write_text("---\nname: test\ndescription: test\n---\n\n工作流拆分 is old term.\n", encoding="utf-8")
            r = _run(["--consistency", str(td)])
            self.assertEqual(r.returncode, 1)
            self.assertIn("W4-OLD", r.stderr)

    def test_w5_old_detection(self):
        with tempfile.TemporaryDirectory() as td:
            td = Path(td)
            (td / "SKILL.md").write_text("---\nname: test\ndescription: test\n---\n\n优化建议 is old term.\n", encoding="utf-8")
            r = _run(["--consistency", str(td)])
            self.assertEqual(r.returncode, 1)
            self.assertIn("W5-OLD", r.stderr)

    def test_version_md_ignored(self):
        with tempfile.TemporaryDirectory() as td:
            td = Path(td)
            (td / "SKILL.md").write_text("---\nname: test\ndescription: test\n---\n\nClean content.\n")
            (td / "VERSION.md").write_text("# Changelog\n\nP-V-E was used before v4.0.\n")
            r = _run(["--consistency", str(td)])
            self.assertEqual(r.returncode, 0, f"VERSION.md should be ignored: {r.stderr}")

    def test_json_output_consistency(self):
        r = _run(["--consistency", str(REPO), "--json"])
        self.assertEqual(r.returncode, 0)
        data = json.loads(r.stdout)
        self.assertEqual(data["status"], "PASS")
        self.assertIn("consistency", data["modes"])


class TestChecklistMode(unittest.TestCase):
    def test_checklist_pass(self):
        r = _run(["--checklist", str(REPO)])
        self.assertEqual(r.returncode, 0, f"Checklist should PASS: {r.stderr}")
        self.assertIn("[CHECKLIST]", r.stdout)

    def test_checklist_missing_gotchas(self):
        with tempfile.TemporaryDirectory() as td:
            td = Path(td)
            dir_name = td.name
            (td / "SKILL.md").write_text(f"---\nname: {dir_name}\ndescription: test\n---\n\nNo gotchas here.\n")
            r = _run(["--checklist", str(td)])
            self.assertEqual(r.returncode, 1)
            self.assertIn("M1", r.stderr)

    def test_checklist_missing_non_goals(self):
        with tempfile.TemporaryDirectory() as td:
            td = Path(td)
            dir_name = td.name
            (td / "SKILL.md").write_text(
                f"---\nname: {dir_name}\ndescription: test\n---\n\n"
                "## Gotchas\n\nSome gotcha.\n\n## Plan-Validate-Handoff\n\nP-V-H mode.\n"
            )
            r = _run(["--checklist", str(td)])
            self.assertEqual(r.returncode, 1)
            self.assertIn("B4", r.stderr)


class TestComboMode(unittest.TestCase):
    def test_checklist_consistency_combo(self):
        r = _run(["--checklist", "--consistency", str(REPO)])
        self.assertEqual(r.returncode, 0, f"Combo should PASS: {r.stderr}")
        self.assertIn("[CHECKLIST]", r.stdout)
        self.assertIn("[CONSISTENCY]", r.stdout)

    def test_quiet_mode(self):
        r = _run(["--spec", str(REPO), "--quiet"])
        self.assertEqual(r.returncode, 0)
        self.assertEqual(r.stdout.strip(), "PASS")


class TestReviewMode(unittest.TestCase):
    def test_review_pass(self):
        review_path = REPO / "examples" / "skill-reviewer-self-review.md"
        if review_path.exists():
            r = _run([str(review_path)])
            self.assertEqual(r.returncode, 0, f"Review should PASS: {r.stderr}")

    def test_review_missing_section(self):
        with tempfile.TemporaryDirectory() as td:
            td = Path(td)
            review_file = td / "review.md"
            review_file.write_text("### 一句话结论\nSome text.\n\n### 复杂度判断\nSome.\n")
            r = _run([str(review_file)])
            self.assertEqual(r.returncode, 1)
            self.assertIn("缺少段落", r.stderr)

    def test_review_no_file_citations(self):
        with tempfile.TemporaryDirectory() as td:
            td = Path(td)
            review_file = td / "review.md"
            sections = [
                "### 一句话结论", "### 复杂度判断", "### 主要优点",
                "### 主要问题", "### 拆分需求识别", "### 整改方向",
                "### 结构性问题总结", "### 总评"
            ]
            review_file.write_text("\n".join(s + "\nNo file refs here." for s in sections), encoding="utf-8")
            r = _run([str(review_file)])
            self.assertEqual(r.returncode, 1)
            self.assertIn("未引用", r.stderr)


class TestVerboseMode(unittest.TestCase):
    def test_verbose_output(self):
        r = _run(["--spec", str(REPO), "--verbose"])
        self.assertEqual(r.returncode, 0)
        self.assertIn("[SPEC] 开始检查", r.stderr)


class TestOffsetOutput(unittest.TestCase):
    def test_offset_and_output(self):
        with tempfile.TemporaryDirectory() as td:
            td = Path(td)
            (td / "SKILL.md").write_text("no frontmatter at all")
            r = _run(["--spec", str(td), "--json", "--offset", "0", "--output", "1"])
            data = json.loads(r.stdout)
            spec_result = data["modes"]["spec"]
            self.assertGreaterEqual(spec_result["total"], 1)
            self.assertEqual(len(spec_result["errors"]), 1)


class TestVersionCheck(unittest.TestCase):
    def test_version_mismatch(self):
        with tempfile.TemporaryDirectory() as td:
            td = Path(td)
            dir_name = td.name
            (td / "SKILL.md").write_text(f"---\nname: {dir_name}\ndescription: test\nmetadata:\n  version: \"1.0\"\n---\n")
            (td / "VERSION.md").write_text("# Changelog\n\n## v2.0 (2026-01-01)\n\nSome change.\n")
            r = _run(["--checklist", str(td)])
            self.assertEqual(r.returncode, 1)
            self.assertIn("不一致", r.stderr)


if __name__ == "__main__":
    unittest.main()
