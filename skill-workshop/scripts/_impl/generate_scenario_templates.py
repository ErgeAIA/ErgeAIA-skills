"""
Generate scenario example drafts from a target Skill's SKILL.md workflows.
"""

from __future__ import annotations

import argparse
from datetime import date
from pathlib import Path
import re
import sys

from .utils import ensure_skill_path, load_markdown_document, load_skill_document

WORKFLOW_HEADER_RE = re.compile(r"^#{2,3}\s+@工作流:\s*(.+?)\s*$", re.MULTILINE)
COMMENT_RE = re.compile(r"<!--\s*@([^:>]+):\s*(.*?)\s*-->")
ACTION_RE = re.compile(r"^-\s+@动作:\s*(.+?)\s*$", re.MULTILINE)
VERSION_ENTRY_RE = re.compile(r"^- \*\*v(\d+\.\d+\.\d+)\*\* \(([^)]+)\) - (.+)$", re.MULTILINE)
ASCII_SLUG_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")


def slugify(value: str) -> str:
    value = value.strip().lower()
    value = re.sub(r"`([^`]*)`", r"\1", value)
    value = re.sub(r"[^\w\s-]", " ", value)
    value = re.sub(r"[\s_]+", "-", value)
    value = re.sub(r"-+", "-", value)
    return value.strip("-") or "scenario"


def slugify_ascii(value: str) -> str:
    value = value.strip().lower()
    value = re.sub(r"`([^`]*)`", r"\1", value)
    value = re.sub(r"[^a-z0-9\s-]", " ", value)
    value = re.sub(r"[\s_]+", "-", value)
    value = re.sub(r"-+", "-", value)
    return value.strip("-")


def normalize_example_slug(workflow: dict) -> str:
    workflow_id = str(workflow.get("workflow_id", "")).strip().lower()
    workflow_id = re.sub(r"^(wf|workflow|step)-", "", workflow_id)
    workflow_id = slugify_ascii(workflow_id)
    if workflow_id:
        return workflow_id

    for candidate in (
        str(workflow.get("scene", "")),
        str(workflow.get("title", "")),
    ):
        ascii_slug = slugify_ascii(candidate)
        if ascii_slug:
            return ascii_slug

    return "scenario-template"


def clean_request_text(value: str) -> str:
    text = value.strip().strip("`").strip()
    text = text.strip("\"'“”‘’")
    text = re.sub(r"^(请|帮我|麻烦你|请你)\s*", "", text)
    return text or value.strip()


def infer_focus_hint(workflow: dict, example_query: str) -> str:
    combined = f"{workflow.get('scene', '')} {workflow.get('title', '')} {example_query}".lower()
    if "skill" in combined:
        return "Skill 结构清晰、关键资源完整、结构化标记规范，并且生成结果可直接继续使用"
    return "判断依据清楚、关键风险明确、输出结果可直接继续使用"


def infer_outcome_hint(workflow: dict, scenario_name: str, example_query: str) -> str:
    combined = f"{workflow.get('scene', '')} {workflow.get('title', '')} {example_query}".lower()
    if "skill" in combined and ("创建" in example_query or "更新" in example_query):
        return "一个可以直接使用的 Skill，以及必要的使用说明、资源说明和下一步建议"
    return f"一份围绕“{scenario_name}”的可直接使用结果，包含结论、关键判断和下一步建议"


def extract_list_value(content: str, label: str) -> str:
    match = re.search(rf"^-\s+{re.escape(label)}:\s*(.+?)\s*$", content, re.MULTILINE)
    if not match:
        return "-"
    return match.group(1).strip()


def bump_patch_version(version: str) -> str:
    match = re.match(r"^(\d+)\.(\d+)\.(\d+)$", version.strip())
    if not match:
        return "0.1.0"
    major, minor, patch = (int(part) for part in match.groups())
    return f"{major}.{minor}.{patch + 1}"


def extract_version_history_lines(content: str) -> list[str]:
    history_match = re.search(
        r"^##\s+(?:版本历史|Version History)\s*$([\s\S]*)",
        content,
        re.MULTILINE,
    )
    if not history_match:
        return []
    return [
        line.strip()
        for line in history_match.group(1).splitlines()
        if VERSION_ENTRY_RE.match(line.strip())
    ]


def get_resolved_project_version(frontmatter: dict) -> str:
    top_level_version = str(frontmatter.get("version", "")).strip()
    if top_level_version:
        return top_level_version

    metadata = frontmatter.get("metadata")
    if isinstance(metadata, dict):
        metadata_version = str(metadata.get("version", "")).strip()
        if metadata_version:
            return metadata_version

    return ""


def resolve_template_version_info(
    file_path: Path, workflow_title: str
) -> tuple[str, list[str], bool]:
    today = date.today().isoformat()
    initial_entry = f"- **v0.1.0** ({today}) - 基于工作流“{workflow_title}”自动生成初始场景示例草稿"
    if not file_path.exists():
        return "0.1.0", [initial_entry], False

    try:
        frontmatter, content = load_markdown_document(file_path)
        current_version = get_resolved_project_version(frontmatter) or "0.1.0"
        next_version = bump_patch_version(current_version)
        history_lines = extract_version_history_lines(content)
    except Exception:
        next_version = "0.1.0"
        history_lines = []

    new_entry = f"- **v{next_version}** ({today}) - 基于工作流“{workflow_title}”重新生成场景示例文档并同步版本"
    merged_history = [new_entry] + history_lines[:4]
    return next_version, merged_history, True


def extract_section(content: str, heading: str) -> list[str]:
    pattern = re.compile(
        rf"^##\s+{re.escape(heading)}\s*$([\s\S]*?)(?=^##\s+|\Z)",
        re.MULTILINE,
    )
    match = pattern.search(content)
    if not match:
        return []

    lines = []
    for raw_line in match.group(1).splitlines():
        stripped = raw_line.strip()
        if stripped.startswith("- "):
            lines.append(stripped[2:].strip())
    return lines


def extract_workflows(content: str) -> list[dict]:
    matches = list(WORKFLOW_HEADER_RE.finditer(content))
    workflows: list[dict] = []
    for index, match in enumerate(matches):
        start = match.start()
        end = matches[index + 1].start() if index + 1 < len(matches) else len(content)
        block = content[start:end]
        metadata_block = block.split("\n### @步骤", 1)[0]
        comments = {key.strip(): value.strip() for key, value in COMMENT_RE.findall(metadata_block)}
        actions = [item.strip() for item in ACTION_RE.findall(block)[:5]]
        title = match.group(1).strip()
        workflows.append({
            "title": title,
            "block": block,
            "scene": comments.get("场景", title),
            "purpose": comments.get("目的", f"完成“{title}”相关任务"),
            "trigger": comments.get("触发条件", ""),
            "workflow_id": comments.get("ID", slugify(title)),
            "actions": actions,
        })
    return workflows


def build_template_content(
    workflow: dict,
    trigger_examples: list[str],
    target_skill_name: str,
    version: str,
    history_lines: list[str],
    is_update: bool,
) -> str:
    scenario_name = workflow["scene"] or workflow["title"]
    scenario_slug = normalize_example_slug(workflow)
    workflow_title = workflow["title"]
    workflow_id = workflow["workflow_id"]
    trigger = workflow["trigger"] or "当用户进入这个场景，且希望直接得到可执行结果时"
    raw_query = trigger_examples[0] if trigger_examples else f"帮我处理{scenario_name}"
    example_query = clean_request_text(raw_query)
    purpose = example_query or workflow["purpose"]
    focus_hint = infer_focus_hint(workflow, example_query)
    outcome_hint = infer_outcome_hint(workflow, scenario_name, example_query)

    info_lines = [
        "- 背景信息: 当前为什么要处理这件事，处于什么阶段，谁会使用结果",
        "- 现有材料: 已有文档、数据、链接、截图、草稿或历史记录",
        "- 关键约束: 时间要求、输出格式、保密边界、篇幅限制或必须遵守的规则",
        "- 判断标准: 你会如何判断结果是否足够好，例如准确、完整、可执行",
        "- 参考样例（可选）: 认可的样例、目标风格或希望对齐的成品",
        "- 其他补充（可选）: 暂时无法归类但可能影响判断的信息",
    ]

    action_summary = ""
    if workflow["actions"]:
        action_summary = "\n".join(f"- {action}" for action in workflow["actions"][:3])
    else:
        action_summary = "- 根据 `SKILL.md` 中对应工作流补充关键动作"

    source_note = (
        f"自动更新自 `{workflow_title}`，并已同步递增模板版本"
        if is_update
        else f"自动生成自 `{workflow_title}`，生成后应按真实使用数据继续人工收敛"
    )

    return f"""---
name: input-template-{scenario_slug}
description: {scenario_name} 场景示例文档。基于 {target_skill_name} 的工作流“{workflow_title}”自动生成的场景示例草稿，用于后续人工收敛。
version: {version}
---

# {scenario_name} 输入模板

<!-- @类型: 场景示例草稿 -->
<!-- @目的: 为高频使用场景提供一份可直接复制、可继续人工收敛的输入示例 -->
<!-- @场景: 由 `{target_skill_name}` 的工作流“{workflow_title}”自动推导出的候选场景 -->
<!-- @触发条件: 当用户反复出现“{scenario_name}”相关诉求时，可将此草稿收敛为正式示例 -->
<!-- @来源工作流: {workflow_id} -->

> **用途**: 用于 `{scenario_name}` 这个高频使用场景，帮助一次性给出高质量输入
> **版本**: v{version}
> **边界**: 本文档不负责工作流路由；工作流由目标 Skill 根据“目的”和“提供的信息”判断
> **来源**: {source_note}

## 适用场景

- 场景名称: `{scenario_name}`
- 对应工作流: `{workflow_title}`
- 一句话需求: `{example_query}`
- 我这次想做什么: `{purpose}`
- 我最关注什么: `{focus_hint}`
- 我希望最终得到什么结果: `{outcome_hint}`

## 建议提供的信息

{chr(10).join(info_lines)}

## 可直接复制输入模板

我现在要处理的场景是：`{scenario_name}`。
这次希望你直接帮我完成：`{purpose}`。
我最关注的是：`{focus_hint}`。
我希望最终拿到的结果是：`{outcome_hint}`。

为避免你来回追问，我先把关键信息一次性给你：

- 背景信息：`{{补充当前背景、所处阶段、结果给谁使用}}`
- 现有材料：`{{补充已有文档、数据、链接、截图、草稿或历史记录}}`
- 关键约束：`{{补充时间要求、输出格式、保密边界或不能突破的限制}}`
- 判断标准：`{{补充你会如何判断这次结果是否足够好}}`
- 参考样例（可选）：`{{补充认可的样例、成品或风格}}`
- 其他补充（可选）：`{{补充其他可能影响判断的信息}}`

如果信息已经足够，请直接进入最合适的处理流程；不要先给我解释有哪些工作流，除非你确实无法判断。

## 来源工作流摘要

{action_summary}

## 裁剪规则（可选）

- 这是自动生成的场景示例草稿，后续应结合真实使用记录继续精简和改写
- 如果差异主要来自目标不同，优先保留同一场景模板，把差异写进 `适用场景` 里的目标描述
- 只有当同一场景真的形成不同输入习惯时，再拆成多个模板

## 版本历史

{chr(10).join(history_lines)}
"""


def generate_templates(
    skill_path: Path, output_dir: Path | None = None, force: bool = False
) -> int:
    skill_ok, skill_message = ensure_skill_path(skill_path)
    if not skill_ok:
        print(f"ERROR: {skill_message}")
        return 1

    frontmatter, content = load_skill_document(skill_path)
    target_skill_name = str(frontmatter.get("name", skill_path.name)).strip() or skill_path.name
    trigger_examples = extract_section(content, "触发示例")
    workflows = extract_workflows(content)
    if not workflows:
        print("ERROR: No `@工作流:` sections found in target SKILL.md")
        return 1

    target_dir = (
        output_dir.resolve()
        if output_dir is not None
        else (skill_path / "references" / "examples").resolve()
    )
    target_dir.mkdir(parents=True, exist_ok=True)

    written_files: list[Path] = []
    for workflow in workflows:
        scenario_slug = normalize_example_slug(workflow)
        file_path = target_dir / f"input-template-{scenario_slug}.md"
        if file_path.exists() and not force:
            print(f"SKIP: {file_path} already exists (use --force to overwrite)")
            continue
        version, history_lines, is_update = resolve_template_version_info(
            file_path, workflow["title"]
        )
        file_path.write_text(
            build_template_content(
                workflow,
                trigger_examples,
                target_skill_name,
                version,
                history_lines,
                is_update,
            ),
            encoding="utf-8",
        )
        written_files.append(file_path)
        print(f"OK: generated {file_path}")

    index_lines = [
        "# 场景示例索引",
        "",
        f"- 目标 Skill: `{target_skill_name}`",
        f"- 示例目录: `{target_dir}`",
        "",
        "## 示例列表",
        "",
        "| 示例文件 | 场景内容 | 对应工作流 |",
        "|---|---|---|",
    ]
    template_files = sorted(
        path for path in target_dir.glob("*.md") if path.is_file() and path.name != "index.md"
    )
    # Reuse already-read content from the generation loop above
    template_contents: dict[str, str] = {}
    for template_path in template_files:
        if template_path in written_files:
            # Just written — read from disk (content was just flushed)
            template_contents[template_path.name] = template_path.read_text(encoding="utf-8")
        else:
            template_contents[template_path.name] = template_path.read_text(encoding="utf-8")
    for template_path in template_files:
        template_content = template_contents[template_path.name]
        scene_text = extract_list_value(template_content, "场景名称").replace("|", "/")
        if scene_text == "-":
            scene_text = template_path.stem.replace("input-template-", "")
        workflow_text = extract_list_value(template_content, "对应工作流").replace("|", "/")
        index_lines.append(f"| `{template_path.name}` | {scene_text} | {workflow_text} |")
    index_path = target_dir / "index.md"
    index_path.write_text("\n".join(index_lines) + "\n", encoding="utf-8")
    print(f"OK: wrote {index_path}")

    if not written_files:
        print("INFO: no new templates were written")
    else:
        print(f"INFO: generated {len(written_files)} scenario template draft(s)")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Generate scenario example drafts from a target skill"
    )
    parser.add_argument("skill_path", help="目标 Skill 目录路径")
    parser.add_argument(
        "--output-dir",
        help="示例输出目录，默认写入 <skill>/references/examples",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="若目标文件已存在则覆盖",
    )
    args = parser.parse_args(argv)

    skill_path = Path(args.skill_path).resolve()
    output_dir = Path(args.output_dir).resolve() if args.output_dir else None
    return generate_templates(skill_path, output_dir=output_dir, force=args.force)


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
