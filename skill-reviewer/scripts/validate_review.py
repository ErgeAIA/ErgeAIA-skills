"""
skill-reviewer 裁判师版自检脚本 v5.2
功能：评审产物校验、仓库 Checklist 扫描、官方 Spec 校验、术语一致性检查。
特性：可操作错误信息、stdout/stderr 分离、输出截断、JSON 输出、正则预编译、文件读取缓存、组合模式、日志级别。
注意：本脚本为只读校验工具，不写入任何文件，无需 --dry-run 支持。
"""

from __future__ import annotations
_VERSION = "5.2"
import argparse
import re
import sys
import json
from pathlib import Path

# ---------- 正则预编译 ----------
SAFE_INPUT_RE = re.compile(r"(?<!\w)input\s*\(")
FILE_CITE_RE = re.compile(r"`[^`]+\.(?:md|py|html|json|ya?ml|txt|sh|ts|js)`")
FILLER_RES = [re.compile(p) for p in [
    r"如果需要.*可以继续", r"希望对你有帮助", r"以上是.*的分析", r"总的来说"
]]
DESC_TECH_RE = re.compile(r"src|api|framework|Next\.js|Vite|\b[a-z]+\.[a-z]+(?:\.[a-z]+)*\b", re.I)
FM_KEY_RE = re.compile(r"^(\w+):")
FM_BLOCK_RE = re.compile(r"^---\s*(.*?)\s*---\s*", re.S)
NAME_FIELD_RE = re.compile(r"^name:\s*(.*)", re.M)
DESC_FIELD_RE = re.compile(r"^description:\s*(.*)", re.M)
GOTCHAS_RE = re.compile(r"##\s*(\d+\.)?\s*(Gotchas|坑点)", re.I)
DESC_LINE_RE = re.compile(r"description:(.*)")
SECTION_CONTENT_RES = [
    (name, re.compile(re.escape(name) + r"([\s\S]*?)(?=###|\Z)"))
    for name in ["主要优点", "主要问题"]
]
NON_GOALS_RE = re.compile(r"##\s*(\d+\.)?\s*(非目标|Non-Goals)", re.I)
TRIGGERS_TOPLEVEL_RE = re.compile(r"^triggers:\s*", re.M)
METADATA_TRIGGERS_RE = re.compile(r"metadata:.*?triggers:", re.S)
NEXT_KEY_CANDIDATES = ["license", "compatibility", "allowed-tools", "metadata"]
VERSION_FIELD_RE = re.compile(r'^\s*version:\s*"?([^"\n]+)"?', re.M)
VERSION_MD_HEADER_RE = re.compile(r'^##\s+v(\S+)', re.M)
H2_RE = re.compile(r"^##\s", re.M)
LIST_RE = re.compile(r"^\s*[-*]\s", re.M)
TRIGGER_WHEN_RE = re.compile(r"trigger-when:", re.I)
ACTIONABLE_ERR_RE = re.compile(r"修复建议|fix|建议[:：]", re.I)
OFFSET_OUTPUT_RE = re.compile(r"--offset|--output")

# ---------- 必需段落预编译 ----------
REQUIRED_SECTIONS = [
    "一句话结论", "复杂度判断", "主要优点", "主要问题",
    "拆分需求识别", "整改方向", "结构性问题总结", "总评"
]
SECTION_REQS = [(name, re.compile(re.escape(name))) for name in REQUIRED_SECTIONS]

# ---------- 顶层不允许的字段 ----------
FORBIDDEN_ROOT_KEYS = {"triggers", "tags"}

# ---------- 术语一致性规则 ----------
CONSISTENCY_RULES = [
    {
        "id": "PVE-PVH",
        "pattern": re.compile(r"Plan-Validate-Execute"),
        "expected": "Plan-Validate-Handoff",
        "desc": "v4.0 已将 P-V-E 改为 P-V-H，发现旧术语",
        "fix": "将 'Plan-Validate-Execute' 替换为 'Plan-Validate-Handoff'（或同时保留两者作为兼容说明）",
    },
    {
        "id": "W4-OLD",
        "pattern": re.compile(r"工作流拆分|工作流重构建议"),
        "expected": "拆分需求识别",
        "desc": "W4 已从'设计拆分方案'改为'识别拆分需求'，发现旧段落名",
        "fix": "将段落名替换为'拆分需求识别'",
    },
    {
        "id": "W5-OLD",
        "pattern": re.compile(r"优化建议|增量建议"),
        "expected": "整改方向",
        "desc": "W5 已从'具体动作模板'改为'整改方向映射'，发现旧段落名",
        "fix": "将段落名替换为'整改方向'",
    },
    {
        "id": "W7-OLD",
        "pattern": re.compile(r"改写建议"),
        "expected": "优化方向",
        "desc": "W7 已将'改写建议'改为'优化方向'，发现旧术语",
        "fix": "将'改写建议'替换为'优化方向'",
    },
    {
        "id": "SECTION7-OLD",
        "pattern": re.compile(r"建议的重构方向"),
        "expected": "结构性问题总结",
        "desc": "报告第 7 段已改为'结构性问题总结'，发现旧段落名",
        "fix": "将'建议的重构方向'替换为'结构性问题总结'",
    },
    {
        "id": "PVE-ABBREV",
        "pattern": re.compile(r"P-V-E(?!-H)"),
        "expected": "P-V-H",
        "desc": "v4.0 已将 P-V-E 缩写改为 P-V-H，发现旧缩写",
        "fix": "将 'P-V-E' 替换为 'P-V-H'",
    },
    {
        "id": "PVE-ARROW",
        "pattern": re.compile(r"Plan\s*→\s*Validate\s*→\s*Execute"),
        "expected": "Plan → Validate → Handoff",
        "desc": "v4.0 已将箭头形式 P→V→E 改为 P→V→H，发现旧术语",
        "fix": "将 'Plan → Validate → Execute' 替换为 'Plan → Validate → Handoff'",
    },
]

def _load_external_rules(script_dir: Path) -> list[dict]:
    yaml_path = script_dir.parent / "references" / "config" / "consistency-rules.yaml"
    if not yaml_path.is_file():
        return []
    try:
        import yaml
    except ImportError:
        return []
    try:
        with open(yaml_path, encoding="utf-8") as f:
            data = yaml.safe_load(f)
        rules = []
        for r in data.get("rules", []):
            rules.append({
                "id": r["id"],
                "pattern": re.compile(r["pattern"]),
                "expected": r["expected"],
                "desc": r["desc"],
                "fix": r["fix"],
            })
        return rules
    except Exception as e:
        print(f"警告：加载外部规则文件 {yaml_path} 失败：{e}，使用内置规则", file=sys.stderr)
        return []

# ---------- 文件读取缓存 ----------
_file_cache: dict[Path, str] = {}
_md_file_cache: dict[Path, list[Path]] = {}

def _read(p: Path) -> str:
    if p in _file_cache:
        return _file_cache[p]
    try:
        content = p.read_text(encoding="utf-8", errors="replace")
    except OSError as e:
        print(f"警告：无法读取 {p}：{e}", file=sys.stderr)
        content = ""
    if "\ufffd" in content:
        print(f"警告：{p} 含非 UTF-8 字符（已替换为 U+FFFD），校验结果可能不完整", file=sys.stderr)
    _file_cache[p] = content
    return content

def _list_md_files(repo: Path) -> list[Path]:
    if repo not in _md_file_cache:
        _md_file_cache[repo] = sorted(repo.rglob("*.md"))
    return _md_file_cache[repo]

def _clear_cache():
    _file_cache.clear()
    _md_file_cache.clear()

def _err(msg: str, fix: str = "") -> str:
    if fix:
        return f"{msg} | 修复建议：{fix}"
    return msg

def _extract_description(text: str, fm_content: str = "") -> tuple[str, bool]:
    found = False
    desc_m = DESC_LINE_RE.search(text)
    if not desc_m:
        return "", found
    found = True
    desc_line = desc_m.group(1).strip().strip('"').strip("'")
    fm_match = FM_BLOCK_RE.match(text) if not fm_content else None
    if fm_match and (desc_line.lstrip().startswith(">") or desc_line.lstrip().startswith("|") or not desc_line.strip()):
        source = fm_content if fm_content else text
        desc_start = source.find("description:")
        next_key_pos = min(
            source.find(k + ":", desc_start + 1) if source.find(k + ":", desc_start + 1) != -1 else float("inf")
            for k in NEXT_KEY_CANDIDATES
        )
        desc_content = source[desc_start:next_key_pos] if next_key_pos != float("inf") else source[desc_start:]
        lines = desc_content.splitlines()[1:]
        return "\n".join(line.lstrip() for line in lines if line.strip()), found
    return desc_line, found

def _is_real_input_call(content: str, match_start: int) -> bool:
    line_start = content.rfind("\n", 0, match_start) + 1
    line_end = content.find("\n", match_start)
    line = content[line_start:line_end] if line_end != -1 else content[line_start:]
    stripped = line.lstrip()
    if stripped.startswith("#"):
        return False
    if "re.compile" in line or "SAFE_INPUT_RE" in line:
        return False
    before = content[:match_start]
    for quote in ['"""', "'''"]:
        count = before.count(quote)
        if count % 2 == 1:
            return False
    return True

# ---------- 评审产物校验 (Review Mode) ----------
def validate_review_output(path: Path) -> list[str]:
    text = _read(path)
    if not text:
        return [_err("文件读取失败或内容为空", f"确认文件存在且可读：{path}")]

    errors = []
    last_pos = -1

    for name, name_re in SECTION_REQS:
        m = name_re.search(text)
        if not m:
            errors.append(_err(
                f"缺少段落：{name}",
                f"在报告中添加 '### {name}' 段落（参考 references/templates/output-template.md）"
            ))
            continue
        if m.start() < last_pos:
            errors.append(_err(
                f"段落顺序错误：{name}",
                f"按 output-template.md 定义的顺序排列：{' → '.join(REQUIRED_SECTIONS)}"
            ))
        last_pos = m.start()

    for section, section_re in SECTION_CONTENT_RES:
        m = section_re.search(text)
        if m and not FILE_CITE_RE.search(m.group(1)):
            errors.append(_err(
                f"{section} 段未引用任何具体文件作为证据",
                f"在 {section} 段中添加反引号包裹的文件名引用，如 `SKILL.md`"
            ))

    for filler_re in FILLER_RES:
        if filler_re.search(text):
            errors.append(_err(
                f"出现水词：{filler_re.pattern}",
                "删除该水词句式，评审报告应冷峻客观"
            ))

    if "意图" not in text and "触发" not in text:
        errors.append(_err(
            "评审报告未包含「意图与触发」专项分析",
            "在主要问题段中添加 description 触发与意图相关的分析"
        ))

    return errors

# ---------- 仓库 Checklist 校验 (Checklist Mode) ----------
def check_checklist(repo: Path) -> list[str]:
    errors = []
    skill_md = repo / "SKILL.md"
    readme_md = repo / "README.md"

    skill_text = _read(skill_md)
    readme_text = _read(readme_md)
    combined_text = skill_text + readme_text

    if not GOTCHAS_RE.search(skill_text):
        errors.append(_err(
            "[M1] 缺少 Gotchas / 坑点段",
            "在 SKILL.md 中添加 '## N. Gotchas（坑点）' 段落，列出环境特定的反直觉事实"
        ))
    if "做法" not in combined_text and "方法论" not in combined_text:
        errors.append(_err(
            "[M6] 缺少「做法优于答案」的方法论指导",
            "在 SKILL.md 中添加方法论指导段落，教 Agent 识别模式而非死记指令"
        ))
    if "Plan-Validate-Handoff" not in combined_text:
        errors.append(_err(
            "[M8] 缺少破坏性操作的 P-V-H 模式说明",
            "在 SKILL.md 中添加 Plan-Validate-Handoff 模式说明段落"
        ))

    if "description:" in skill_text:
        desc_line, _ = _extract_description(skill_text)
        if desc_line and not DESC_TECH_RE.search(desc_line):
            errors.append(_err(
                "[T3] description 疑似缺失「技术特征」或「项目环境」触发维度",
                "在 description 中添加技术锚点（如：Python 脚本、JSON 输出、特定框架名）和项目环境（如：Skill 仓库、src/ 目录）"
            ))

    if not NON_GOALS_RE.search(skill_text):
        errors.append(_err(
            "[B4] 缺少非目标 (Non-Goals) 段",
            "在 SKILL.md 中添加 '## N. 非目标 (Non-Goals)' 段落，明确列出本 Skill 不处理的场景"
        ))

    if TRIGGERS_TOPLEVEL_RE.search(skill_text):
        if not METADATA_TRIGGERS_RE.search(skill_text):
            errors.append(_err(
                "[B3] triggers 字段在顶层，必须在 metadata 内部",
                "将 triggers 字段移入 metadata 内部，如 'metadata:\\n  triggers: [...]'"
            ))

    if not H2_RE.search(skill_text):
        errors.append(_err(
            "[S2] SKILL.md 缺少结构化标记（H2 标题）",
            "在 SKILL.md 中使用 ## 标题划分段落，提升可解析性"
        ))
    elif not LIST_RE.search(skill_text):
        errors.append(_err(
            "[S2] SKILL.md 缺少列表标记",
            "在 SKILL.md 中使用 - 或 * 列表组织条目，提升可解析性"
        ))

    refs_dir = repo / "references"
    if refs_dir.is_dir():
        for ref_file in refs_dir.rglob("*.md"):
            ref_text = _read(ref_file)
            if ref_text and not TRIGGER_WHEN_RE.search(ref_text):
                rel = ref_file.relative_to(repo)
                errors.append(_err(
                    f"[C4] {rel} 缺少 trigger-when 加载指引",
                    f"在 {rel} 的 frontmatter 中添加 trigger-when 字段，说明何时加载此文件"
                ))

    scripts_dir = repo / "scripts"
    has_runnable_script = False
    if scripts_dir.is_dir():
        for script in scripts_dir.iterdir():
            if script.suffix == ".py" and script.name != "__init__.py":
                has_runnable_script = True
                content = _read(script)
                if SAFE_INPUT_RE.search(content):
                    real_hit = any(_is_real_input_call(content, m.start()) for m in SAFE_INPUT_RE.finditer(content))
                    if real_hit:
                        errors.append(_err(
                            f"[P3] {script.name} 含交互式调用，Agent 执行必挂",
                            f"将 {script.name} 中的交互式调用改为命令行参数（argparse）"
                        ))
                if "argparse" not in content and "--help" not in content:
                    errors.append(_err(
                        f"[P4] {script.name} 缺少 --help 自描述",
                        f"在 {script.name} 中添加 argparse 并实现 --help"
                    ))
                if "sys.stderr" not in content:
                    errors.append(_err(
                        f"[P6] {script.name} 未分离 stdout/stderr",
                        f"在 {script.name} 中将错误/诊断信息输出到 sys.stderr，数据输出到 stdout"
                    ))
                if not ACTIONABLE_ERR_RE.search(content):
                    errors.append(_err(
                        f"[P5] {script.name} 错误信息疑似不可操作",
                        f"在 {script.name} 的错误信息中添加修复建议（如 '修复建议：...' 或 'fix: ...'）"
                    ))
                if not OFFSET_OUTPUT_RE.search(content) and len(content.splitlines()) > 50:
                    errors.append(_err(
                        f"[P7] {script.name} 疑似缺少输出截断支持",
                        f"在 {script.name} 中添加 --offset / --output 参数支持大量输出翻页"
                    ))
    if not has_runnable_script and scripts_dir.is_dir():
        errors.append(_err(
            "[I2] scripts/ 目录存在但无可独立运行的 Python 脚本",
            "在 scripts/ 中添加至少一个可独立运行的 .py 脚本"
        ))

    for vid, kw in [("V1", "成功判定"), ("V2", "自检标准"), ("V3", "产出检查")]:
        if kw not in skill_text:
            errors.append(_err(
                f"[{vid}] 未发现验证闭环描述：{kw}",
                f"在 SKILL.md 验证闭环段落中添加 {kw} 相关描述"
            ))
    if "trigger-test-set" not in skill_text and "正面集" not in skill_text and "负面集" not in skill_text:
        errors.append(_err(
            "[V4] 未发现评估测试集描述",
            "在 SKILL.md 验证闭环段落中添加 V4 评估测试集相关描述（参考 references/templates/trigger-test-set.md）"
        ))
    if "可机器判定" not in skill_text and "machine-checkable" not in skill_text:
        errors.append(_err(
            "[V5] 未发现评估断言可机器判定描述",
            "在 SKILL.md 验证闭环段落中添加 V5 评估断言可机器判定相关描述"
        ))

    version_md = repo / "VERSION.md"
    if version_md.is_file():
        vm_text = _read(version_md)
        vm_m = VERSION_MD_HEADER_RE.search(vm_text)
        if vm_m:
            vm_ver = vm_m.group(1)
            sv_m = VERSION_FIELD_RE.search(skill_text)
            if sv_m:
                skill_ver = sv_m.group(1).strip()
                if skill_ver != vm_ver:
                    errors.append(_err(
                        f"SKILL.md version '{skill_ver}' 与 VERSION.md 最新版本 '{vm_ver}' 不一致",
                        f"将 SKILL.md metadata.version 更新为 '{vm_ver}' 或在 VERSION.md 中添加 '{skill_ver}' 条目"
                    ))

    return errors

# ---------- 术语一致性检查 (Consistency Mode) ----------
CONSISTENCY_IGNORE_FILES = {"VERSION.md"}

def check_consistency(repo: Path) -> list[str]:
    errors = []
    md_files = _list_md_files(repo)

    for md_file in md_files:
        rel = md_file.relative_to(repo)
        if str(rel) in CONSISTENCY_IGNORE_FILES:
            continue
        text = _read(md_file)
        lines = text.splitlines()
        for rule in CONSISTENCY_RULES:
            for m in rule["pattern"].finditer(text):
                line_no = text[:m.start()].count("\n") + 1
                line_text = lines[line_no - 1] if line_no <= len(lines) else ""
                if "v4.0 前" in line_text or "旧术语" in line_text:
                    continue
                errors.append(_err(
                    f"[{rule['id']}] {rel}:{line_no} — {rule['desc']}（发现 '{m.group()}'，期望 '{rule['expected']}'）",
                    rule["fix"]
                ))

    return errors

# ---------- 官方 Spec 校验 (Spec Mode) ----------
ALLOWED_ROOT_KEYS = {"name", "description", "license", "compatibility", "metadata", "allowed-tools"}
EXPECTED_KEY_ORDER = ["name", "description", "license", "compatibility", "metadata", "allowed-tools"]
REQUIRED_KEYS = ["name", "description"]

def check_spec(repo: Path) -> tuple[str, list[str]]:
    failures = []
    skill_md = repo / "SKILL.md"
    text = _read(skill_md)

    fm_match = FM_BLOCK_RE.match(text)
    if not fm_match:
        return "FAIL", [_err("缺少 frontmatter 或格式错误", "在 SKILL.md 文件首行添加 '---' 分隔的 YAML frontmatter")]

    fm_content = fm_match.group(1)
    top_keys = []
    for line in fm_content.splitlines():
        m = FM_KEY_RE.match(line)
        if m:
            top_keys.append(m.group(1))

    for key in top_keys:
        if key not in ALLOWED_ROOT_KEYS:
            failures.append(_err(
                f"未知顶层属性：{key}",
                f"移除 '{key}' 或将其移入 metadata 内部"
            ))
        if key in FORBIDDEN_ROOT_KEYS:
            failures.append(_err(
                f"'{key}' 必须放在 metadata 内部，不能作为顶层属性",
                f"将 '{key}' 移入 metadata 映射内部"
            ))

    for key in REQUIRED_KEYS:
        if key not in top_keys:
            failures.append(_err(
                f"缺少必需字段：{key}",
                f"在 frontmatter 中添加 '{key}' 字段"
            ))
    allowed_keys_in_order = [k for k in EXPECTED_KEY_ORDER if k in top_keys]
    if allowed_keys_in_order != top_keys:
        failures.append(_err(
            f"字段顺序错误。当前顺序：{' → '.join(top_keys)}。正确顺序：name → description → license → compatibility → metadata → allowed-tools",
            "按 name → description → license → compatibility → metadata → allowed-tools 顺序排列 frontmatter 字段"
        ))

    name_m = NAME_FIELD_RE.search(fm_content)
    name = name_m.group(1).strip().strip('"').strip("'") if name_m else ""
    repo_name = repo.resolve().name
    if not name:
        failures.append(_err("name 字段缺失", "在 frontmatter 中添加 name 字段"))
    else:
        if name != repo_name:
            failures.append(_err(
                f"目录名 '{repo_name}' 与 name '{name}' 不符",
                f"将 name 字段值改为 '{repo_name}' 或重命名目录为 '{name}'"
            ))
        if re.search(r'[A-Z]', name):
            failures.append(_err(
                f"name '{name}' 含大写字符（必须为 hyphen-case）",
                f"将 name 改为全小写：'{name.lower()}'"
            ))
        if name.startswith('-') or name.endswith('-'):
            failures.append(_err(
                f"name '{name}' 以连字符开头或结尾",
                "移除 name 首尾的连字符"
            ))
        if '--' in name:
            failures.append(_err(
                f"name '{name}' 含连续连字符",
                "将连续连字符替换为单个连字符"
            ))
        if len(name) > 64:
            failures.append(_err(
                f"name 长度 {len(name)} 超过 64 字符上限",
                "缩短 name 字段值至 64 字符以内"
            ))

    desc, desc_found = _extract_description(text, fm_content)
    if desc_found:
        if "<" in desc:
            failures.append(_err(
                "description 字段严禁包含尖括号 < >",
                "移除 description 中的 HTML 标签或尖括号，改用其他标记方式"
            ))
        if not desc.strip():
            failures.append(_err(
                "description 字段为空",
                "在 description 中填写有实际内容的描述"
            ))
        if len(desc) > 1024:
            failures.append(_err(
                f"description 长度 {len(desc)} 超过 1024 字符上限",
                "精简 description 内容至 1024 字符以内"
            ))
    else:
        failures.append(_err("description 字段缺失", "在 frontmatter 中添加 description 字段"))

    return ("PASS" if not failures else "FAIL"), failures

# ---------- 入口函数 ----------
def main():
    parser = argparse.ArgumentParser(
        description="skill-reviewer 裁判师版自检工具",
        epilog="模式说明：默认=评审产物校验  --checklist=仓库快速扫描  --spec=官方规范校验  --consistency=术语一致性检查\n可组合：--checklist --consistency 同时运行多个模式"
    )
    parser.add_argument("target", help="目标文件或目录")
    parser.add_argument("--checklist", action="store_true", help="运行仓库快速扫描模式（覆盖 M/T/P/V/B 关键项）")
    parser.add_argument("--spec", action="store_true", help="运行官方 Spec 模式")
    parser.add_argument("--consistency", action="store_true", help="运行术语一致性检查（检测 v4.0 重构后的旧术语残留）")
    parser.add_argument("--json", action="store_true", help="以 JSON 格式输出结果")
    parser.add_argument("--offset", type=int, default=0, help="跳过前 N 条错误（用于输出截断）")
    parser.add_argument("--output", type=int, default=0, help="最多输出 N 条错误（0=全部）")
    parser.add_argument("--quiet", action="store_true", help="静默模式：只输出 PASS/FAIL，不输出错误详情")
    parser.add_argument("--verbose", action="store_true", help="详细模式：输出每个模式的检查过程")
    parser.add_argument("--version", action="version", version=f"%(prog)s {_VERSION}")
    args = parser.parse_args()

    target_path = Path(args.target)
    if not target_path.exists():
        print(f"错误：找不到路径 {args.target}", file=sys.stderr)
        sys.exit(2)

    _clear_cache()

    external_rules = _load_external_rules(Path(__file__).resolve().parent)
    if external_rules:
        global CONSISTENCY_RULES
        CONSISTENCY_RULES = CONSISTENCY_RULES + external_rules

    modes_requested = []
    if args.spec:
        modes_requested.append("spec")
    if args.checklist:
        modes_requested.append("checklist")
    if args.consistency:
        modes_requested.append("consistency")
    if not modes_requested:
        modes_requested.append("review")

    all_results: dict[str, dict] = {}
    overall_status = "PASS"

    for mode in modes_requested:
        mode_result = {"status": "PASS", "errors": []}
        if args.verbose:
            print(f"[{mode.upper()}] 开始检查...", file=sys.stderr)

        if mode == "spec":
            res, fails = check_spec(target_path)
            mode_result["status"], mode_result["errors"] = res, fails
        elif mode == "consistency":
            errs = check_consistency(target_path)
            if errs:
                mode_result["status"], mode_result["errors"] = "FAIL", errs
        elif mode == "checklist":
            errs = check_checklist(target_path)
            if errs:
                mode_result["status"], mode_result["errors"] = "FAIL", errs
        elif mode == "review":
            errs = validate_review_output(target_path)
            if errs:
                mode_result["status"], mode_result["errors"] = "FAIL", errs

        if mode_result["status"] == "FAIL":
            overall_status = "FAIL"

        mode_result["total"] = len(mode_result["errors"])
        errors = mode_result["errors"]
        if args.offset:
            errors = errors[args.offset:]
        if args.output:
            errors = errors[:args.output]
        mode_result["displayed"] = len(errors)
        mode_result["errors"] = errors
        all_results[mode] = mode_result

    if args.json:
        print(json.dumps({"status": overall_status, "modes": all_results}, ensure_ascii=False, indent=2))
    else:
        if args.quiet:
            print(overall_status)
        else:
            for mode, mode_result in all_results.items():
                if mode_result["status"] == "FAIL":
                    for e in mode_result["errors"]:
                        print(f"- [{mode.upper()}] {e}", file=sys.stderr)
                    if args.offset or args.output:
                        print(f"（[{mode.upper()}] 显示 {mode_result['displayed']}/{mode_result['total']} 条，使用 --offset / --output 翻页）", file=sys.stderr)
                else:
                    print(f"[{mode.upper()}] {args.target} 通过校验")

    sys.exit(1 if overall_status == "FAIL" else 0)

if __name__ == "__main__":
    main()
