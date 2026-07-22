#!/usr/bin/env python3
from __future__ import annotations
import ast,re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
SKIP={'.git','.venv','venv','node_modules','dist','build','__pycache__','.pytest_cache','.mypy_cache'}
PATTERNS={'private-key':re.compile(r'-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----'),'github-token':re.compile(r'\bgh[pousr]_[A-Za-z0-9]{30,}\b'),'aws-access-key':re.compile(r'\bAKIA[0-9A-Z]{16}\b')}
SUFFIXES={'.py','.md','.toml','.yml','.yaml','.json','.txt','.sh','.cmd','.js'}
def main()->int:
    findings=[]
    for path in ROOT.rglob('*'):
        if not path.is_file() or any(part in SKIP for part in path.parts) or path.suffix.lower() not in SUFFIXES: continue
        text=path.read_text(encoding='utf-8',errors='replace')
        for name,pattern in PATTERNS.items():
            if pattern.search(text): findings.append(f'{path.relative_to(ROOT)}: high-confidence secret pattern: {name}')
        if path.suffix=='.py' and 'tests' not in path.parts:
            try: tree=ast.parse(text)
            except SyntaxError as exc: findings.append(f'{path.relative_to(ROOT)}:{exc.lineno}: syntax error'); continue
            for node in ast.walk(tree):
                if isinstance(node,ast.Call):
                    name=node.func.id if isinstance(node.func,ast.Name) else (node.func.attr if isinstance(node.func,ast.Attribute) else '')
                    if name in {'eval','exec'}: findings.append(f'{path.relative_to(ROOT)}:{node.lineno}: dangerous dynamic execution: {name}')
    if findings: print('\n'.join(findings)); return 1
    print('Security scan: no high-confidence secrets or forbidden dynamic execution patterns found.'); return 0
if __name__=='__main__': raise SystemExit(main())
