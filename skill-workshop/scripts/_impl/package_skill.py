"""
Skill Packager - Creates a distributable .skill file of a skill folder

Usage:
    python scripts/skill_cli.py package <path/to/skill-folder> [output-directory]

Example:
    python scripts/skill_cli.py package skills/public/my-skill
    python scripts/skill_cli.py package skills/public/my-skill ./dist
"""

from pathlib import Path
import sys
import zipfile

from .quick_validate import validate_skill
from ._gate import require_plan
from .utils import ensure_skill_path, run_skill_validate


def should_skip_path(rel_to_skill: Path, file_path: Path) -> bool:
    if any(
        part in {"dist", "__pycache__", "benchmark", "benchmarks", "runs"}
        for part in rel_to_skill.parts
    ):
        return True
    if any(
        (part.startswith("eval-") and part[5:].isdigit())
        or (part.startswith("run-") and part[4:].isdigit())
        for part in rel_to_skill.parts
    ):
        return True
    if file_path.suffix == ".pyc":
        return True
    if file_path.name.startswith("."):
        return True
    return False


def iter_packaged_files(skill_path: Path):
    for file_path in skill_path.rglob("*"):
        if not file_path.is_file():
            continue
        rel_to_skill = file_path.relative_to(skill_path)
        if should_skip_path(rel_to_skill, file_path):
            continue
        yield file_path, rel_to_skill


def find_newer_source_files(skill_path: Path, package_path: Path) -> list[Path]:
    if not package_path.exists():
        return []

    package_mtime = package_path.stat().st_mtime
    newer_files: list[Path] = []
    for file_path, _ in iter_packaged_files(skill_path):
        if file_path.stat().st_mtime > package_mtime:
            newer_files.append(file_path)
    return newer_files


def print_preflight_summary() -> None:
    print("🧾 Preflight summary:")
    print("   - spec checks cover frontmatter shape, required name/description, and optional field types")
    print("   - project checks cover version metadata (version or metadata.version) and version sync")
    print("   - scaffold placeholders such as TODO and YYYY-MM-DD are removed")
    print("   - target skill validate_skill.py passes when scripts/validate_skill.py is present")
    print("   - semantic markup includes workflow, steps, metadata comments, and @动作 items")
    print("   - local Markdown links, same-file anchors, and cross-file anchors resolve")
    print("   - fix missing file before missing anchor; use available/maybe hints when present")
    print("   - treat body-length warnings as a cue to move long details into references/")
    print("   - if the published package is stale, refresh it by repackaging before release\n")


def package_skill(skill_path, output_dir=None):
    """
    Package a skill folder into a .skill file.

    Args:
        skill_path: Path to the skill folder
        output_dir: Optional output directory for the .skill file (defaults to current directory)

    Returns:
        Path to the created .skill file, or None if error
    """
    skill_path = Path(skill_path).resolve()

    skill_ok, skill_message = ensure_skill_path(skill_path)
    if not skill_ok:
        print(f"❌ Error: {skill_message}")
        return None

    # Run validation before packaging
    print("🔍 Validating skill...")
    valid, message = validate_skill(skill_path)
    if not valid:
        print(f"❌ Validation failed: {message}")
        print("   Please fix the validation errors before packaging.")
        return None
    print(f"✅ {message}\n")

    print("🧪 Running target skill validation...")
    validate_ok, validate_message = run_skill_validate(skill_path)
    if not validate_ok:
        print(f"❌ {validate_message}")
        return None
    print(f"✅ {validate_message}\n")

    # Determine output location
    skill_name = skill_path.resolve().name
    if output_dir:
        output_path = Path(output_dir).resolve()
        output_path.mkdir(parents=True, exist_ok=True)
    else:
        output_path = Path.cwd()

    skill_filename = output_path / f"{skill_name}.skill"

    existing_dist_package = skill_path / "dist" / f"{skill_name}.skill"
    newer_files = find_newer_source_files(skill_path, existing_dist_package)
    if newer_files:
        print(
            "⚠️  Warning: published package may be stale; source files are newer than dist package."
        )
        print(f"   Existing package: {existing_dist_package}")
        print(f"   Newer source example: {newer_files[0]}")
        print("   Repackaging will refresh the published artifact.\n")

    print_preflight_summary()

    # Create the .skill file (zip format)
    try:
        with zipfile.ZipFile(skill_filename, "w", zipfile.ZIP_DEFLATED) as zipf:
            # Walk through the skill directory
            for file_path, _ in iter_packaged_files(skill_path):
                arcname = file_path.relative_to(skill_path.parent)
                zipf.write(file_path, arcname)
                print(f"  Added: {arcname}")

        print(f"\n✅ Successfully packaged skill to: {skill_filename}")
        return skill_filename

    except Exception as e:
        print(f"❌ Error creating .skill file: {e}")
        return None


def main(argv: list[str] | None = None) -> int:
    import argparse

    parser = argparse.ArgumentParser(
        prog="skill_cli.py package",
        description="Package a skill folder into a distributable .skill file",
    )
    parser.add_argument("skill_path", help="Path to the skill folder")
    parser.add_argument("output_dir", nargs="?", default=None, help="Output directory (default: cwd)")
    parser.add_argument(
        "--write",
        action="store_true",
        help="actually write the .skill package (default: dry-run preview)",
    )
    parser.add_argument(
        "--plan",
        default=None,
        help="Plan-gate: path to five-section plan file (goal/scope/params/stop/rollback)",
    )
    parser.add_argument(
        "--plan-text",
        default=None,
        help="Plan-gate quick lane with a one-line plan (HUMANS ONLY; AI must use --plan)",
    )
    args = parser.parse_args(argv)

    if not args.write:
        # Dry-run 预览（目标驱动脚本协议：写文件命令默认不落盘）
        sp = Path(args.skill_path)
        ok, msg = ensure_skill_path(sp)
        valid, vmsg = validate_skill(sp.resolve()) if ok else (False, msg)
        target_name = sp.resolve().name + ".skill"
        target = (Path(args.output_dir).resolve() if args.output_dir else Path.cwd()) / target_name
        print("[dry-run] package preview")
        print(f"  target: {target}")
        print(f"  validation: {'PASS' if valid else 'FAIL — ' + vmsg}")
        print("  add --write to actually package (plan-gate applies)")
        return 0 if valid else 1

    # Plan-gate（目标驱动脚本协议）：写文件动作需先出示计划。
    require_plan(args.plan, args.plan_text, "package")

    skill_path = args.skill_path
    output_dir = args.output_dir

    print(f"📦 Packaging skill: {skill_path}")
    if output_dir:
        print(f"   Output directory: {output_dir}")
    print()

    result = package_skill(skill_path, output_dir)

    if result:
        return 0
    return 1
