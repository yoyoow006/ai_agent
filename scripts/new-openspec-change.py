#!/usr/bin/env python3
"""Create and check the repository's standard OpenSpec artifacts."""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TEMPLATE_ROOT = ROOT / "openspec" / "templates"
PLACEHOLDER = re.compile(r"\{\{[^\n{}]+\}\}")
SAFE_NAME = re.compile(r"^[a-z0-9][a-z0-9-]{2,63}$")


def templates_for(mode: str, with_design: bool) -> list[str]:
    files = ["proposal.md", "spec.md", "tasks.md"]
    if mode == "strict" or with_design:
        files.append("design.md")
    return files


def fail(message: str) -> int:
    print(f"FAIL: {message}", file=sys.stderr)
    return 1


def create(name: str, mode: str, target: Path, with_design: bool) -> int:
    if not SAFE_NAME.fullmatch(name):
        return fail("变更名必须匹配 [a-z0-9][a-z0-9-]{2,63}")
    if mode not in {"standard", "strict"}:
        return fail("模式必须是 standard 或 strict")
    if target.exists() and (not target.is_dir() or any(target.iterdir())):
        return fail(f"目标目录必须为空：{target}")
    target.mkdir(parents=True, exist_ok=True)
    spec_dir = target / "specs" / name
    spec_dir.mkdir(parents=True, exist_ok=False)
    status = "待确认计划" if mode == "standard" else "待确认规范"
    for filename in templates_for(mode, with_design):
        source = TEMPLATE_ROOT / filename
        destination = target / filename if filename != "spec.md" else spec_dir / filename
        content = source.read_text(encoding="utf-8")
        content = content.replace("{{MODE}}", "标准" if mode == "standard" else "严格")
        content = content.replace("{{STATUS}}", status)
        destination.write_text(content, encoding="utf-8")
    print(target)
    return 0


def check_file(path: Path, required: list[str]) -> list[str]:
    errors: list[str] = []
    try:
        content = path.read_text(encoding="utf-8")
    except OSError as exc:
        return [f"{path}: {exc}"]
    if PLACEHOLDER.search(content):
        errors.append(f"{path}: 仍含未替换占位符")
    for marker in required:
        if marker not in content:
            errors.append(f"{path}: 缺少 {marker}")
    if path.name == "tasks.md":
        commands = re.findall(r"`([^`\n]+)`", content)
        if not commands:
            errors.append(f"{path}: 缺少单行验证命令")
        if "本地整合策略" not in content:
            errors.append(f"{path}: 缺少本地整合策略")
    if path.name == "spec.md" and not re.search(r"\*\*WHEN\*\*.*\n- \*\*THEN\*\*", content):
        errors.append(f"{path}: 缺少 WHEN/THEN 场景")
    return errors


def check(change: Path) -> int:
    if not change.is_dir():
        return fail(f"变更目录不存在：{change}")
    files = [change / "proposal.md", change / "tasks.md"]
    specs = sorted((change / "specs").glob("*/spec.md")) if (change / "specs").is_dir() else []
    files.extend(specs)
    if (change / "design.md").exists():
        files.append(change / "design.md")
    if not specs:
        return fail("缺少 specs/<能力>/spec.md")
    required = {
        "proposal.md": ["模式:", "状态:", "## Why", "## What Changes", "## Impact", "## Scope", "## Acceptance"],
        "tasks.md": ["- [ ]", "## 本地整合策略"],
        "spec.md": ["## Requirements", "#### Scenario:", "**WHEN**", "**THEN**"],
        "design.md": ["## 目标与约束", "## 方案与替代方案", "## 验证矩阵"],
    }
    errors = [error for path in files for error in check_file(path, required[path.name])]
    if errors:
        for error in errors:
            print(f"FAIL: {error}", file=sys.stderr)
        return 1
    print(f"PASS: OpenSpec 模板结构（{len(files)} files）")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="command", required=True)
    create_parser = sub.add_parser("create")
    create_parser.add_argument("name")
    create_parser.add_argument("--mode", choices=["standard", "strict"], required=True)
    create_parser.add_argument("--target", type=Path, default=None)
    create_parser.add_argument("--with-design", action="store_true")
    check_parser = sub.add_parser("check")
    check_parser.add_argument("change", type=Path)
    args = parser.parse_args()
    if args.command == "create":
        target = args.target or ROOT / "openspec" / "changes" / args.name
        return create(args.name, args.mode, target, args.with_design)
    return check(args.change)


if __name__ == "__main__":
    raise SystemExit(main())
