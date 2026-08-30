#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# ///
"""版本单源化辅助：以 VERSION.md 顶部最新版本为唯一真源，同步写入 SKILL.md frontmatter.version。

用法：
    python scripts/_impl/sync_version.py <skill_dir>

无第三方依赖（仅标准库）。不交互、不修改 VERSION.md，只改 SKILL.md 的 metadata.version。
退出码：0 成功 / 1 未找到版本 / 2 写入失败。
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

VERSION_RE = re.compile(r"^##\s+v(\d+\.\d+\.\d+)", re.MULTILINE)
FRONTMATTER_VERSION_RE = re.compile(r'^(?P<indent>\s*)version:\s*"(?P<ver>[^"]+)"\s*$', re.MULTILINE)


def read_latest_version(version_md: Path) -> str | None:
    text = version_md.read_text(encoding="utf-8")
    m = VERSION_RE.search(text)
    return m.group(1) if m else None


def sync(skill_dir: Path) -> int:
    skill_md = skill_dir / "SKILL.md"
    version_md = skill_dir / "VERSION.md"
    if not skill_md.exists():
        print(f"[sync_version] 缺失 SKILL.md: {skill_md}")
        return 2
    if not version_md.exists():
        print(f"[sync_version] 缺失 VERSION.md: {version_md}")
        return 2

    latest = read_latest_version(version_md)
    if not latest:
        print("[sync_version] 未能从 VERSION.md 解析到版本号")
        return 1

    content = skill_md.read_text(encoding="utf-8")
    m = FRONTMATTER_VERSION_RE.search(content)
    if not m:
        print("[sync_version] SKILL.md frontmatter 未找到 metadata.version")
        return 2

    if m.group("ver") == latest:
        print(f"[sync_version] 已一致: {latest}（无需修改）")
        return 0

    new_content = FRONTMATTER_VERSION_RE.sub(
        lambda _: f'{m.group("indent")}version: "{latest}"', content, count=1
    )
    skill_md.write_text(new_content, encoding="utf-8")
    print(f"[sync_version] 已同步 SKILL.md version: {m.group('ver')} -> {latest}")
    return 0


def main() -> int:
    if len(sys.argv) < 2:
        print("用法: python scripts/_impl/sync_version.py <skill_dir>")
        return 2
    return sync(Path(sys.argv[1]))


if __name__ == "__main__":
    raise SystemExit(main())
