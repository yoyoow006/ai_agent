#!/usr/bin/env python3
"""Validate or render bounded project-registration drafts."""
from __future__ import annotations
import argparse, json
from pathlib import Path
from project_facts import load_registry, InputError

def render(args: argparse.Namespace) -> int:
    data = json.loads(Path(args.input).read_text(encoding="utf-8"))
    required = {"name", "path", "card", "server", "module", "main_class", "source_path", "description"}
    missing = sorted(required - set(data))
    if missing:
        raise InputError("missing fields: " + ", ".join(missing))
    out = Path(args.output_dir); out.mkdir(parents=True, exist_ok=True)
    card = out / Path(data["card"]).name
    if card.exists() and not args.force:
        raise InputError(f"refusing to overwrite {card}; use --force")
    entry = {"name": data["name"], "path": data["path"], "build": data.get("build", "maven"), "card": f"kb/projects/{card.name}", "search_roots": ["."], "applications": [{k: data[k] for k in ("server", "module", "main_class", "source_path")}], "business_terms": data.get("business_terms", [])}
    (out / "registry-entry.json").write_text(json.dumps(entry, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    card.write_text(f"# {data['name']} 项目卡\n\n## 职责\n\n- 负责：{data['description']}\n\n## 高频入口\n\n- `{data['main_class']}` → `{data['path']}/{data['source_path']}`\n\n## 证据与维护\n\n- 事实来源：待维护者补充权威来源。\n", encoding="utf-8")
    (out / "rules-index-entry.md").write_text(f"| 项目登记：{data['name']} | `{data['path']}` | {data['description']} | {data['name']} |\n", encoding="utf-8")
    print(out / "registry-entry.json")
    print(card)
    return 0

def main() -> int:
    p = argparse.ArgumentParser(); sub = p.add_subparsers(dest="command", required=True)
    v = sub.add_parser("validate"); v.add_argument("--workspace", required=True)
    r = sub.add_parser("render"); r.add_argument("--input", required=True, type=Path); r.add_argument("--output-dir", required=True, type=Path); r.add_argument("--force", action="store_true")
    args = p.parse_args()
    if args.command == "validate":
        load_registry(args.workspace); print("VALID registry"); return 0
    return render(args)
if __name__ == "__main__":
    try: raise SystemExit(main())
    except (InputError, OSError, json.JSONDecodeError) as exc:
        raise SystemExit(f"ERROR: {exc}")
