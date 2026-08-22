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
    argv = list(sys.argv[1:] if argv is None else argv)
    if argv and argv[0] in {"-h", "--help"}:
        print(
            "Usage: python scripts/skill_cli.py package <path/to/skill-folder> [output-directory]"
        )
        print("\nExample:")
        print("  python scripts/skill_cli.py package skills/public/my-skill")
        print("  python scripts/skill_cli.py package skills/public/my-skill ./dist")
        return 0
    if len(argv) < 1:
        print(
            "Usage: python scripts/skill_cli.py package <path/to/skill-folder> [output-directory]"
        )
        print("\nExample:")
        print("  python scripts/skill_cli.py package skills/public/my-skill")
        print("  python scripts/skill_cli.py package skills/public/my-skill ./dist")
        return 1

    skill_path = argv[0]
    output_dir = argv[1] if len(argv) > 1 else None

    print(f"📦 Packaging skill: {skill_path}")
    if output_dir:
        print(f"   Output directory: {output_dir}")
    print()

    result = package_skill(skill_path, output_dir)

    if result:
        return 0
    return 1
