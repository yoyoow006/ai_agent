#!/usr/bin/env python3
"""Validate the registry or render project-registration drafts in an explicit directory."""
from __future__ import annotations

import argparse
import json
from pathlib import Path, PurePosixPath
import sys

from project_facts import InputError, load_registry, _business_terms, _relative, _string


def relative(value, label, *, allow_dot=False):
    value = _relative(value, label, allow_dot=allow_dot)
    if '\\' in value or '\0' in value or value != str(PurePosixPath(value)):
        raise InputError(f'{label} must be a normalized relative path')
    return value


def text(value, label):
    value = _string(value, label)
    if not value.strip() or '\0' in value:
        raise InputError(f'{label} must be non-empty text')
    return value


def draft(data):
    required = {'name', 'path', 'build', 'card', 'description'}
    if not isinstance(data, dict) or not required.issubset(data):
        raise InputError('required fields: ' + ', '.join(sorted(required)))
    name = text(data['name'], 'name')
    description = text(data['description'], 'description')
    card = relative(data['card'], 'card')
    card_path = PurePosixPath(card)
    if card_path.parent not in (PurePosixPath('.'), PurePosixPath('kb/projects')):
        raise InputError('card must be a filename or kb/projects/<filename>')
    card_name = card_path.name
    if card_path.suffix != '.md' or card_name in {'registry-entry.json', 'rules-index-entry.md'}:
        raise InputError('card must be a distinct Markdown filename')
    app_fields = {'server', 'module', 'main_class', 'source_path'}
    if 'applications' in data:
        if app_fields.intersection(data):
            raise InputError('use applications or legacy application fields, not both')
        apps = data['applications']
    elif app_fields.issubset(data):
        apps = [{key: data[key] for key in app_fields}]
    else:
        raise InputError('applications must be explicit (an empty list is allowed)')
    if not isinstance(apps, list):
        raise InputError('applications must be a list')
    checked = []
    for app in apps:
        if not isinstance(app, dict) or set(app) != app_fields:
            raise InputError('application requires server, module, main_class, source_path')
        checked.append({
            'server': text(app['server'], 'server'),
            'module': relative(app['module'], 'module', allow_dot=True),
            'main_class': text(app['main_class'], 'main_class'),
            'source_path': relative(app['source_path'], 'source_path'),
        })
    roots = data.get('search_roots', ['.'])
    if not isinstance(roots, list) or not roots:
        raise InputError('search_roots must be a non-empty list')
    entry = {
        'name': name, 'path': relative(data['path'], 'path'),
        'build': text(data['build'], 'build'), 'card': f'kb/projects/{card_name}',
        'search_roots': [relative(root, 'search root', allow_dot=True) for root in roots],
        'applications': checked,
        'business_terms': _business_terms(data.get('business_terms', []), name),
    }
    entries = '\n'.join(f"- `{app['main_class']}` → `{entry['path']}/{app['source_path']}`" for app in checked)
    card_text = f'# {name} 项目卡\n\n## 职责\n\n- 负责：{description}\n\n## 高频入口\n\n{entries or "- 库模块，无应用入口。"}\n\n## 证据与维护\n\n- 事实来源：待维护者补充权威来源。\n'
    return {
        'registry-entry.json': json.dumps(entry, ensure_ascii=False, indent=2) + '\n',
        card_name: card_text,
        'rules-index-entry.md': f'| 项目登记：{name} | `{entry["path"]}` | {description} | {name} |\n',
    }


def render(args):
    outputs = draft(json.loads(args.input.read_text(encoding='utf-8')))
    out = args.output_dir.absolute()
    if any(parent.is_symlink() for parent in (out, *out.parents)):
        raise InputError('output directory must not contain symlinks')
    if out.exists() and not out.is_dir():
        raise InputError('output directory is not a directory')
    for name in outputs:
        target = out / name
        if target.is_symlink() or (target.exists() and not target.is_file()):
            raise InputError(f'unsafe output: {target}')
        if target.exists() and not args.force:
            raise InputError(f'refusing to overwrite {target}; use --force')
    out.mkdir(parents=True, exist_ok=True)
    for name, content in outputs.items():
        with (out / name).open('w' if args.force else 'x', encoding='utf-8') as stream:
            stream.write(content)
        print(out / name)
    return 0


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest='command', required=True)
    validate = commands.add_parser('validate')
    validate.add_argument('--workspace', required=True)
    renderer = commands.add_parser('render')
    renderer.add_argument('--input', required=True, type=Path)
    renderer.add_argument('--output-dir', required=True, type=Path)
    renderer.add_argument('--force', action='store_true')
    args = parser.parse_args()
    try:
        if args.command == 'validate':
            load_registry(args.workspace)
            print('VALID registry')
            return 0
        return render(args)
    except (InputError, OSError, ValueError) as error:
        print(f'ERROR: {error}', file=sys.stderr)
        return 2


if __name__ == '__main__':
    raise SystemExit(main())
