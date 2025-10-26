#!/usr/bin/env python3
import re, sys, os
from datetime import datetime

SRC='discussion/ChatHistory.md'
APPLY=True

text=open(SRC,'r',encoding='utf-8').read().splitlines()
start_re=re.compile(r'^(?P<fence>`{3,})(?:\s*md)?\s*\{(?P<attrs>[^}]*)\}\s*$')
end_re=lambda n: re.compile(r'^`{%d}\s*$'%n)
kv_re=re.compile(r'(\w+)\s*=\s*"([^"]*)"|(\w+)\s*=\s*([^\s\}]+)')

def parse_attrs(s):
    d={}
    for m in kv_re.finditer(s):
        if m.group(1): d[m.group(1)]=m.group(2)
        else: d[m.group(3)]=m.group(4)
    return d

def role_of(attrs):
    by=attrs.get('by','')
    cr=attrs.get('cr','')
    if by=='assistant' or cr.startswith('assistant'): return 'assistant'
    if cr=='user' or ('cr' not in attrs and by!='assistant'): return 'user'
    return 'unknown'

# heuristics: ordered list (label, patterns)
HEUR=[
  ('module-spec_tool', [r'\bSPEC_TOOL\b']),
  ('chatindex-structured', [r'ChatIndex', r'Index']),
  ('fencing-escalation', [r'fenced', r'反引号', r'外层加长', r'fence']),
  ('trash-policy', [r'\.trush', r'入库', r'frontmatter', r'删除', r'命名规范']),
  ('intent-structure', [r'intent', r'结构化', r'三段']),
  ('record-policy-no-record', [r'No-Record', r'不记录']),
  ('timestamp-format', [r'时间戳', r'UTC', r'Z\b', r'本地时区']),
  ('rollback-remediation', [r'回滚', r'恢复', r'remediation', r'整档']),
  ('spec-update-policy', [r'规范更新', r'SPEC', r'Role-Specific']),
  ('chathistory-format', [r'ChatHistory', r'格式迁移', r'fenced 结构']),
  ('validation-report', [r'ValidationReport', r'校验', r'validate']),
]

def suggest_situation(body):
    for label, pats in HEUR:
        for pat in pats:
            if re.search(pat, body, flags=re.I):
                return label
    # default fallback
    return 'general-discussion'

# parse blocks
blocks=[]; i=0; n=len(text)
while i<n:
    m=start_re.match(text[i])
    if not m:
        i+=1; continue
    fence=m.group('fence'); fl=len(fence)
    attrs_raw=m.group('attrs'); attrs=parse_attrs(attrs_raw)
    start_i=i; i+=1; body=[]; er=end_re(fl)
    while i<n and not er.match(text[i]): body.append(text[i]); i+=1
    if i<n: i+=1
    blocks.append({'fence_len':fl,'attrs':attrs,'start_line':start_i,'body':'\n'.join(body)})

changed=0
out=[]; i=0; bi=0
while i<n:
    m=start_re.match(text[i])
    if not m:
        out.append(text[i]); i+=1; continue
    b=blocks[bi]; bi+=1
    fl=b['fence_len']; attrs=b['attrs']; body=b['body']
    # Determine if needs situation
    if 'situation' not in attrs:
        label=suggest_situation(body)
        attrs['situation']=label
        changed+=1
    # reconstruct header; preserve existing keys order (ts first if present)
    keys=list(attrs.keys())
    # prefer order: ts, situation, by, cr
    order=['ts','situation','by','cr']
    keys=sorted(keys, key=lambda k: (order.index(k) if k in order else 99, k))
    header='```md {' + ' '.join(f'{k}="{attrs[k]}"' for k in keys) + '}'
    # write header
    out.append(header)
    i+=1
    # write body
    er=end_re(fl)
    while i<n and not er.match(text[i]):
        out.append(text[i]); i+=1
    if i<n: i+=1
    out.append('```')

if APPLY:
    with open(SRC,'w',encoding='utf-8') as f:
        f.write('\n'.join(out)+('\n' if not out or out[-1] != '' else ''))
print(f'Annotated situations (changed blocks: {changed}).')
