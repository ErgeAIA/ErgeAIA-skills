# -*- coding: utf-8 -*-
"""skill-workshop 自身回归测试（unittest，零第三方依赖）。

运行（在 skill-workshop/ 下）：
  python -m unittest discover -s scripts/tests -t .
  python scripts/tests/test_validator.py

存在理由：v2.2.0 及更早的 validator 用词法统计（意图词表、触发词计数、引号词数量）
代理 description 的语义质量，实测出现两类反向结果——裸词表被判合规高分、自然中文描述
被判硬错误（证据见 CHANGELOG v2.3.0）。本文件锁住修正后的契约：
**CLI 只判结构，语义质量归评审/优化模式**。
"""
from __future__ import annotations

import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

TESTS_DIR = Path(__file__).resolve().parent
SKILL_DIR = TESTS_DIR.parent.parent
SCRIPTS_DIR = SKILL_DIR / "scripts"
CLI = SCRIPTS_DIR / "skill_cli.py"
sys.path.insert(0, str(SCRIPTS_DIR))

from _impl.quick_validate import (  # noqa: E402
    validate_description_format,
    validate_description_symbols,
)

# 推荐句式（什么时候用 + 解决什么 + 边界），无引号关键词
DESC_A = ("当用户需要提交代码、管理分支或处理 Git 操作时，提供规范的 Git 工作流指导，"
          "并在可能改写历史或删除数据的危险操作前要求确认。")
# 裸词表：格式合法但语义质量低，validator 不得因词多给出任何「更好」的判定
DESC_B = "Git commit branch merge push pull rebase PR review audit check validate"
# 自然中文、且刻意不含旧词表里的意图动词（提取/评审/校验/create/review…）
DESC_C = ("当用户把写好的 Markdown 贴过来、要一份能直接粘进微信公众号编辑器的排版结果时，"
          "负责把源文转成带主题样式的编辑器 HTML。")


def write_skill(root: Path, name: str, description: str, *, body: str = "# 占位\n",
                changelog: bool = True, raw_description_line: str | None = None) -> Path:
    """造一个最小可校验技能目录（结构合规，只让 description 成为变量）。"""
    d = root / name
    d.mkdir(parents=True, exist_ok=True)
    desc_line = raw_description_line if raw_description_line is not None else f'description: "{description}"'
    (d / "SKILL.md").write_text(
        "---\n"
        f"name: {name}\n"
        f"{desc_line}\n"
        "metadata:\n"
        '  author: t\n'
        '  version: "1.0.0"\n'
        "---\n\n"
        f"# {name}\n\n{body}\n",
        encoding="utf-8",
    )
    if changelog:
        (d / "CHANGELOG.md").write_text(
            "# 版本历史\n\n## [1.0.0] - 2026-01-01\n\n- 初始版本。\n", encoding="utf-8")
    return d


def run_cli(command: str, target: Path) -> subprocess.CompletedProcess:
    # 子进程默认继承控制台编码（Windows 常为 cp936），中文 finding 会变成乱码，
    # 那时 assertNotIn 类断言会「因为读不到而通过」——固定 UTF-8 才有意义。
    env = {**__import__("os").environ, "PYTHONIOENCODING": "utf-8"}
    return subprocess.run(
        [sys.executable, str(CLI), command, str(target)],
        capture_output=True, text=True, encoding="utf-8", errors="replace",
        env=env, check=False)


class DescriptionStructureContract(unittest.TestCase):
    """CLI 只判结构：A / B / C 三者结构判定必须一致，且不再输出任何计数。"""

    def setUp(self):
        self.root = Path(tempfile.mkdtemp(prefix="sw-test-"))
        self.addCleanup(shutil.rmtree, self.root, True)

    def test_three_styles_are_structurally_equal(self):
        results = {}
        for tag, desc in (("a", DESC_A), ("b", DESC_B), ("c", DESC_C)):
            skill = write_skill(self.root, f"demo-{tag}", desc)
            proc = run_cli("validate", skill)
            blob = proc.stdout + proc.stderr
            desc_lines = [ln for ln in blob.splitlines() if "description" in ln.lower()
                          or "Description" in ln]
            results[tag] = (proc.returncode, desc_lines)
        for tag, (rc, lines) in results.items():
            self.assertEqual(rc, 0, f"{tag} 结构校验应通过：{lines}")
            self.assertEqual([l for l in lines if "symbol" in l or "format" in l], [],
                             f"{tag} 不该出现 description 报错：{lines}")

    def test_no_lexical_counters_anywhere(self):
        skill = write_skill(self.root, "demo-count", DESC_B)
        blob = (run_cli("validate", skill).stdout + run_cli("validate", skill).stderr)
        for banned in ("个触发词", "核心意图关键词", "引号内触发词", "疑似裸词表"):
            self.assertNotIn(banned, blob, f"词法计数判据必须已废除，但仍出现：{banned}")

    def test_intent_keyword_table_is_gone(self):
        import _impl.quick_validate as qv
        for removed in ("INTENT_KEYWORDS",):
            self.assertFalse(hasattr(qv, removed), f"{removed} 应已删除")

    def test_placeholder_and_multiline_are_errors(self):
        for desc, needle in (
            (DESC_A + " {{TODO_TARGET}}", "占位符"),
            ("待补 TODO 再写", "占位符"),
        ):
            ok, msg, sev = validate_description_format({"description": desc})
            self.assertFalse(ok, desc)
            self.assertEqual(sev, "error")
            self.assertIn(needle, msg)

    def test_block_scalar_multiline_is_error(self):
        ok, msg, _sev = validate_description_format({"description": "第一行\n第二行"})
        self.assertFalse(ok)
        self.assertIn("单行", msg)

    def test_overlong_is_error(self):
        ok, msg, _sev = validate_description_format({"description": "字" * 1025})
        self.assertFalse(ok)
        self.assertIn("1024", msg)

    def test_missing_or_non_string(self):
        self.assertFalse(validate_description_format({})[0])
        self.assertFalse(validate_description_format({"description": ["a"]})[0])


class CliNeverCrashesAndStillReports(unittest.TestCase):
    """反例必须被「报告」而不是把 CLI 打崩；同时证明中文 finding 确实可读回（正向对照）。"""

    def setUp(self):
        self.root = Path(tempfile.mkdtemp(prefix="sw-crash-"))
        self.addCleanup(shutil.rmtree, self.root, True)

    def test_unquoted_description_with_colon_reports_instead_of_traceback(self):
        # 未加引号 + 含 `: ` → YAML 解析失败（v2.3.0 前 main() 解包 2 元组直接 ValueError）
        d = write_skill(self.root, "demo-unquoted", "", raw_description_line="description: 当用户要提交代码时给指导，Not for: 通用审查。")
        proc = run_cli("validate", d)
        blob = proc.stdout + proc.stderr
        self.assertNotIn("Traceback", blob, blob[:400])
        self.assertNotIn("ValueError", blob, blob[:400])
        self.assertEqual(proc.returncode, 1, blob[:400])
        self.assertIn("双引号", blob, f"应给出可执行的修复建议：{blob[:400]}")

    def test_positive_control_chinese_findings_are_decodable(self):
        # 若这条断言失败，说明上面所有 assertNotIn 都在拿乱码比较（形同虚设）
        d = write_skill(self.root, "demo-backslash", "路径 C:\\\\tmp 下的技能。")
        blob = run_cli("validate", d).stdout + run_cli("validate", d).stderr
        self.assertIn("反斜杠", blob, blob[:400])

    def test_overlong_description_still_reports_symbol_problem(self):
        long_desc = "字" * 1030
        d = write_skill(self.root, "demo-overlong", "",
                        raw_description_line=f"description: {long_desc}")
        proc = run_cli("validate", d)
        blob = proc.stdout + proc.stderr
        self.assertIn("too long", blob)
        self.assertIn("双引号", blob, "超长时不得连带跳过其余结构检查")


class SymbolSeverityContract(unittest.TestCase):
    """YAML 真实风险留 HARD；纯风格符号降为 advisory。"""

    def test_hard_only_for_parse_risk(self):
        problems, advisories = validate_description_symbols(
            'description: 处理 A/B 与 C: 边界')
        self.assertTrue(any("双引号" in p for p in problems), problems)
        self.assertFalse(any("斜杠" in p for p in problems), problems)
        self.assertFalse(any("冒号" in p for p in problems), problems)
        self.assertEqual(advisories, [], "未加引号时风格项不该叠加报错，双引号问题优先")

    def test_backslash_is_hard(self):
        problems, _adv = validate_description_symbols('description: "路径 C:\\\\tmp 与 A/B"')
        self.assertTrue(any("反斜杠" in p for p in problems), problems)

    def test_slash_and_halfwidth_colon_are_advisory(self):
        problems, advisories = validate_description_symbols(
            'description: "当用户要处理 GitHub Actions: 部署或 A/B 实验时给出指导。"')
        self.assertEqual(problems, [], f"斜杠与半角冒号不得再判硬错：{problems}")
        self.assertTrue(any("斜杠" in a for a in advisories), advisories)
        self.assertTrue(any("半角冒号" in a for a in advisories), advisories)

    def test_not_for_colon_is_exempt(self):
        problems, advisories = validate_description_symbols(
            'description: "当用户要提交代码时给出指导。Not for: 通用代码审查。"')
        self.assertEqual(problems, [])
        self.assertFalse(any("半角冒号" in a for a in advisories), advisories)


class SpecOrderIsAdvisory(unittest.TestCase):
    def setUp(self):
        self.root = Path(tempfile.mkdtemp(prefix="sw-spec-"))
        self.addCleanup(shutil.rmtree, self.root, True)

    def test_wrong_field_order_does_not_block(self):
        d = write_skill(self.root, "demo-order", DESC_A)
        text = (d / "SKILL.md").read_text(encoding="utf-8")
        # 把 metadata 提到 description 之前，制造顺序不一致
        reordered = text.replace('description: "' + DESC_A + '"\n', "", 1)
        reordered = reordered.replace("name: demo-order\n",
                                      'name: demo-order\nmetadata:\n  author: t\n  version: "1.0.0"\n', 1)
        reordered = reordered.replace("metadata:\n  author: t\n  version: \"1.0.0\"\n---",
                                      'description: "' + DESC_A + '"\n---', 1)
        (d / "SKILL.md").write_text(reordered, encoding="utf-8")
        proc = run_cli("spec", d)
        self.assertEqual(proc.returncode, 0, f"顺序不应阻塞：{proc.stderr}")
        self.assertIn("顺序", proc.stderr)

    def test_angle_bracket_stays_hard_but_is_labeled_convention(self):
        d = write_skill(self.root, "demo-angle", "当用户要 <插件> 时提供指导。")
        proc = run_cli("spec", d)
        self.assertEqual(proc.returncode, 1)
        self.assertIn("本仓约定", proc.stderr)

    def test_missing_frontmatter_field_blocks(self):
        d = write_skill(self.root, "demo-noname", DESC_A)
        (d / "SKILL.md").write_text(
            "---\n" + f'description: "{DESC_A}"\n' + "---\n\n# demo-noname\n", encoding="utf-8")
        self.assertEqual(run_cli("spec", d).returncode, 1)


ARCHETYPES = {
    "simple-only-skillmd": {"files": ["SKILL.md"], "desc": DESC_A},
    "single-responsibility": {"files": ["SKILL.md", "references/x.md"], "desc": DESC_C},
    "multi-responsibility": {"files": ["SKILL.md", "references/x.md", "references/y.md"],
                             "desc": DESC_B},
    "script-heavy": {"files": ["SKILL.md", "scripts/run.py"], "desc": DESC_A},
    "reference-heavy": {"files": ["SKILL.md"] + [f"references/r{i}.md" for i in range(6)],
                        "desc": DESC_C},
    "very-short-desc": {"files": ["SKILL.md"], "desc": "当用户要提交代码时给出 Git 指导。"},
    "long-but-good": {"files": ["SKILL.md"], "desc": DESC_A + " " + DESC_C},
    "keyword-stuffed-poor": {"files": ["SKILL.md"],
                             "desc": "review audit check inspect validate verify assess "
                                     "evaluate examine vet test 评审 审计 校验 检查 评测"},
    "sparse-but-good": {"files": ["SKILL.md", "CHANGELOG.md"], "desc": DESC_C},
}


class ArchetypesNeverPenalisedForMissingAssets(unittest.TestCase):
    """缺 assets / scripts / eval / Gotchas 不是缺陷；结构合规就应通过。"""

    def setUp(self):
        self.root = Path(tempfile.mkdtemp(prefix="sw-arch-"))
        self.addCleanup(shutil.rmtree, self.root, True)

    def test_all_archetypes_pass_structure(self):
        for name, cfg in ARCHETYPES.items():
            with self.subTest(archetype=name):
                d = write_skill(self.root, name, cfg["desc"])
                for rel in cfg["files"]:
                    if rel in ("SKILL.md", "CHANGELOG.md"):
                        continue
                    p = d / rel
                    p.parent.mkdir(parents=True, exist_ok=True)
                    p.write_text("---\n" f"trigger-when: 需要时\nname: {p.stem}\n"
                                 "description: 占位\n---\n\n# 占位\n"
                                 if rel.endswith(".md") else "print('ok')\n", encoding="utf-8")
                proc = run_cli("validate", d)
                blob = proc.stdout + proc.stderr
                for banned in ("缺少 scripts", "必须有 eval", "缺 Gotchas", "建议增加示例",
                               "触发词", "核心意图关键词"):
                    self.assertNotIn(banned, blob, f"{name} 因缺资产或被词法计数评判：{banned}")
                self.assertEqual(proc.returncode, 0, f"{name} 结构应通过：{blob}")


if __name__ == "__main__":
    unittest.main(verbosity=2)
