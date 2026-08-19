"""Shared utilities for kz-skill-creator scripts."""

from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys

try:
    import yaml  # type: ignore
except Exception:
    yaml = None


def extract_frontmatter_text(content: str) -> str:
    lines = content.splitlines()
    if not lines or lines[0].strip() != "---":
        raise ValueError("SKILL.md missing frontmatter (no opening ---)")

    for index, line in enumerate(lines[1:], start=1):
        if line.strip() == "---":
            return "\n".join(lines[1:index])

    raise ValueError("SKILL.md missing frontmatter (no closing ---)")


def parse_simple_yaml(text: str) -> dict:
    root = {}
    current_key = None
    current_container = None

    def parse_scalar(value: str):
        value = value.strip()
        if not value:
            return ""
        if (value.startswith('"') and value.endswith('"')) or (
            value.startswith("'") and value.endswith("'")
        ):
            return value[1:-1]
        return value

    for raw_line in text.splitlines():
        line = raw_line.rstrip("\n")
        if not line.strip():
            continue
        if line.lstrip().startswith("#"):
            continue

        indent = len(line) - len(line.lstrip(" "))
        stripped = line.strip()

        if indent == 0:
            current_key = None
            current_container = None

            if ":" not in stripped:
                continue

            key, value = stripped.split(":", 1)
            key = key.strip()
            value = value.strip()

            if value == "":
                root[key] = {}
                current_key = key
                current_container = root[key]
                continue

            root[key] = parse_scalar(value)
            continue

        if current_key is None:
            continue

        if stripped.startswith("- "):
            if not isinstance(current_container, list):
                root[current_key] = []
                current_container = root[current_key]
            current_container.append(parse_scalar(stripped[2:]))
            continue

        if ":" in stripped:
            if not isinstance(current_container, dict):
                root[current_key] = {}
                current_container = root[current_key]
            key, value = stripped.split(":", 1)
            current_container[key.strip()] = parse_scalar(value)
            continue

    return root


def ensure_skill_path(skill_path: Path) -> tuple[bool, str]:
    skill_path = Path(skill_path)
    if not skill_path.exists():
        return False, f"Skill folder not found: {skill_path}"
    if not skill_path.is_dir():
        return False, f"Skill path is not a directory: {skill_path}"

    skill_md = skill_path / "SKILL.md"
    if not skill_md.exists():
        return False, f"SKILL.md not found: {skill_md}"

    return True, "Skill path is valid"


def load_json_file(json_path: Path, label: str = "JSON file") -> tuple[object | None, str]:
    json_path = Path(json_path)
    try:
        raw = json_path.read_text(encoding="utf-8")
    except FileNotFoundError:
        return None, f"{label} not found: {json_path}"
    except IsADirectoryError:
        return None, f"{label} path is a directory: {json_path}"
    except OSError as exc:
        return None, f"Failed to read {label.lower()}: {exc}"

    try:
        return json.loads(raw), f"{label} loaded"
    except json.JSONDecodeError as exc:
        return (
            None,
            f"{label} is not valid JSON: {exc.msg} (line {exc.lineno}, column {exc.colno})",
        )


def load_skill_document(skill_path: Path) -> tuple[dict, str]:
    skill_md = skill_path / "SKILL.md"
    return load_markdown_document(skill_md)


def load_markdown_document(markdown_path: Path) -> tuple[dict, str]:
    markdown_path = Path(markdown_path)
    content = markdown_path.read_text(encoding="utf-8")
    frontmatter_text = extract_frontmatter_text(content)

    if yaml is not None:
        frontmatter = yaml.safe_load(frontmatter_text)
        if not isinstance(frontmatter, dict):
            raise ValueError(f"Frontmatter must be a YAML dictionary: {markdown_path}")
        return frontmatter, content

    frontmatter = parse_simple_yaml(frontmatter_text)
    if not isinstance(frontmatter, dict):
        raise ValueError(f"Frontmatter must be a YAML dictionary: {markdown_path}")
    return frontmatter, content


def parse_skill_md(skill_path: Path) -> tuple[str, str, str]:
    """Parse a SKILL.md file, returning (name, description, full_content)."""
    frontmatter, content = load_skill_document(skill_path)
    name = str(frontmatter.get("name", "")).strip()
    description = str(frontmatter.get("description", "")).strip()
    return name, description, content


def validate_eval_set(eval_set: list[dict]) -> tuple[bool, str]:
    """Validate eval-set structure before running expensive evals."""
    if not isinstance(eval_set, list):
        return False, "Eval set must be a JSON array"
    if not eval_set:
        return False, "Eval set must not be empty"

    seen_queries: set[str] = set()
    errors: list[str] = []
    for index, item in enumerate(eval_set, start=1):
        prefix = f"item {index}"
        if not isinstance(item, dict):
            errors.append(f"{prefix}: must be an object")
            continue

        if "query" not in item:
            errors.append(f"{prefix}: missing 'query'")
        elif not isinstance(item["query"], str):
            errors.append(f"{prefix}: 'query' must be a string")
        elif not item["query"].strip():
            errors.append(f"{prefix}: 'query' must not be empty")
        elif item["query"] in seen_queries:
            errors.append(f"{prefix}: duplicate query '{item['query']}'")
        else:
            seen_queries.add(item["query"])

        if "should_trigger" not in item:
            errors.append(f"{prefix}: missing 'should_trigger'")
        elif not isinstance(item["should_trigger"], bool):
            errors.append(f"{prefix}: 'should_trigger' must be a boolean")

    if errors:
        preview = "\n  - ".join(errors[:10])
        more = ""
        if len(errors) > 10:
            more = f"\n  - ... and {len(errors) - 10} more"
        return False, "Invalid eval set:\n  - " + preview + more

    return True, "Eval set is valid"


def load_and_validate_eval_set(eval_set_path: Path) -> tuple[list[dict] | None, str]:
    data, message = load_json_file(eval_set_path, label="Eval set")
    if data is None:
        return None, message

    valid, validation_message = validate_eval_set(data)
    if not valid:
        return None, validation_message

    return data, "Eval set is valid"


def run_skill_validate(skill_path: Path) -> tuple[bool, str]:
    """Run target skill's validate_skill.py if present."""
    validate_script = skill_path / "scripts" / "validate_skill.py"
    if not validate_script.exists():
        return True, "No scripts/validate_skill.py found; skipping target skill validation"

    result = subprocess.run(
        [sys.executable, str(validate_script), "--skill", "."],
        cwd=skill_path,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        details = result.stdout.strip() or result.stderr.strip() or "no output"
        return False, f"Target skill validation failed: {details}"

    details = result.stdout.strip() or "validate_skill.py passed"
    return True, f"Target skill validation passed: {details}"
