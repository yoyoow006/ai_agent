#!/usr/bin/env python3
from __future__ import annotations
import argparse, os, re, shutil, sys, tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]; TEMPLATE_ROOT=ROOT/'openspec/templates'; PLACEHOLDER=re.compile(r'\{\{[^\n{}]+\}\}'); SAFE_NAME=re.compile(r'^[a-z0-9][a-z0-9-]{2,63}$'); VERSION='模板版本: 1'
def fail(m): print(f'FAIL: {m}',file=sys.stderr); return 1
def templates_for(mode,design): return ['proposal.md','spec.md','tasks.md']+(['design.md'] if mode=='strict' or design else [])
def create(name,mode,target,design):
 if target is None:return fail('必须显式提供 --target 空目录')
 if not SAFE_NAME.fullmatch(name):return fail('变更名必须匹配 [a-z0-9][a-z0-9-]{2,63}')
 if target.is_symlink():return fail('目标目录不得为 symlink')
 if target.exists() and (not target.is_dir() or any(target.iterdir())):return fail(f'目标目录必须为空：{target}')
 parent=target.parent; parent.mkdir(parents=True,exist_ok=True); stage=Path(tempfile.mkdtemp(prefix=f'.{target.name}.',dir=parent))
 try:
  (stage/'specs'/name).mkdir(parents=True); status='待确认计划' if mode=='standard' else '待确认规范'
  for fn in templates_for(mode,design):
   src=TEMPLATE_ROOT/fn; dst=stage/fn if fn!='spec.md' else stage/'specs'/name/fn
   dst.write_text(src.read_text(encoding='utf-8').replace('{{MODE}}','标准' if mode=='standard' else '严格').replace('{{STATUS}}',status),encoding='utf-8')
  if target.exists():
   backup=Path(tempfile.mkdtemp(prefix=f'.{target.name}.backup.',dir=parent)); backup.rmdir(); os.replace(target,backup)
   try: os.replace(stage,target)
   except Exception: os.replace(backup,target); raise
   shutil.rmtree(backup)
  else: os.replace(stage,target)
 except Exception as e: shutil.rmtree(stage,ignore_errors=True); return fail(f'创建失败且已清理：{e}')
 print(target); return 0
def check_file(path,required,new):
 try:c=path.read_text(encoding='utf-8')
 except OSError as e:return [f'{path}: {e}']
 es=[]
 if new and PLACEHOLDER.search(c):es.append(f'{path}: 仍含未替换占位符')
 for m in required:
  if m not in c:es.append(f'{path}: 缺少 {m}')
 if path.name=='proposal.md' and new:
  if not re.search(r'^模式:\s*(标准|严格)\s*$',c,re.M):es.append(f'{path}: 模式非法')
 if path.name=='spec.md' and new:
  if 'ADDED Requirements' not in c:es.append(f'{path}: 缺少 ADDED Requirements')
  for b in re.split(r'#### Scenario:',c)[1:]:
   m=re.search(r'\*\*WHEN\*\*\s*(.*)\n- \*\*THEN\*\*\s*(.*)',b)
   if not m or not m.group(1).strip() or not m.group(2).strip():es.append(f'{path}: WHEN/THEN 不得为空')
 if path.name=='tasks.md' and new:
  for l in c.splitlines():
   if l.startswith('  - [ ]') and '验证' in l and (not re.search(r'`([^`\n]+)`',l)):es.append(f'{path}: 验证命令必须是单行且非空')
  if not re.search(r'预期结果[:：]', c) or '## 本地整合策略' not in c:es.append(f'{path}: 缺少验证预期或整合策略')
 return es
def check(change):
 if not change.is_dir() or change.is_symlink():return fail(f'变更目录不存在或不安全：{change}')
 specs=sorted((change/'specs').glob('*/spec.md')) if (change/'specs').is_dir() else []
 if not specs:return fail('缺少 specs/<能力>/spec.md')
 files=[change/'proposal.md',change/'tasks.md',*specs]; d=change/'design.md'
 if d.exists():files.append(d)
 marker=(change/'proposal.md').read_text(encoding='utf-8',errors='ignore').startswith(VERSION)
 req={'proposal.md':['模式:','状态:','## Why','## What Changes','## Impact','## Scope','## Acceptance','## Unverified scope','## Residual risk'],'tasks.md':['- [ ]','## 本地整合策略'],'spec.md':['## ADDED Requirements','#### Scenario:','**WHEN**','**THEN**'],'design.md':['## 目标与约束','## 方案与替代方案','## 验证矩阵']}
 es=[e for p in files for e in check_file(p,req[p.name],marker)]
 if marker and re.search(r'^模式:\s*严格', (change/'proposal.md').read_text(encoding='utf-8'),re.M) and not d.exists():es.append('严格模式必须包含 design.md')
 if es:
  [print(f'FAIL: {e}',file=sys.stderr) for e in es]; return 1
 print(f'PASS: OpenSpec 模板结构（{len(files)} files）'); return 0
def check_templates():
 es=[]
 for n in ('proposal.md','spec.md','tasks.md','design.md'):
  p=TEMPLATE_ROOT/n
  if not p.is_file() or VERSION not in p.read_text(encoding='utf-8'):es.append(f'模板缺少 {VERSION}：{p}')
 if es:[print(f'FAIL: {e}',file=sys.stderr) for e in es]; return 1
 print('PASS: OpenSpec 模板'); return 0
def main():
 p=argparse.ArgumentParser();s=p.add_subparsers(dest='command',required=True);c=s.add_parser('create');c.add_argument('name');c.add_argument('--mode',choices=['standard','strict'],required=True);c.add_argument('--target',type=Path);c.add_argument('--with-design',action='store_true');q=s.add_parser('check');q.add_argument('change',type=Path);s.add_parser('check-templates');a=p.parse_args();return create(a.name,a.mode,a.target,a.with_design) if a.command=='create' else check_templates() if a.command=='check-templates' else check(a.change)
if __name__=='__main__':raise SystemExit(main())
