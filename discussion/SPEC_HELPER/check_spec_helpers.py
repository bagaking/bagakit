#!/usr/bin/env python3
import os, re, sys
from datetime import datetime
ROOT='discussion/SPEC_HELPER'
SPEC='discussion/SPEC.md'
TRUSH='discussion/.trush'
os.makedirs(TRUSH, exist_ok=True)

# Gather helper references from SPEC (must be mentioned to be compliant)
spec_text=open(SPEC,'r',encoding='utf-8').read()
refs=set(m.group(1) for m in re.finditer(r'discussion/SPEC_HELPER/([\w\-\.]+)', spec_text))

files=[f for f in os.listdir(ROOT) if os.path.isfile(os.path.join(ROOT,f))]
noncompliant=[]
for f in files:
    if f == 'check_spec_helpers.py':
        continue
    if not re.search(r'\.(py|sh|js|ts|rb|pl|go|rs)$', f):
        noncompliant.append((f,'non_script_artifact'))
        continue
    if f not in refs:
        noncompliant.append((f,'not_referenced_in_SPEC'))

APPLY='--apply' in sys.argv
stamp=datetime.now().astimezone().strftime('%Y%m%dT%H%M%S%z')
for f,reason in noncompliant:
    if not APPLY:
        continue
    src=os.path.join(ROOT,f)
    dst=os.path.join(TRUSH, f"{stamp}.{f}.non_compliant_spec_helper_{reason}.md")
    with open(dst,'w',encoding='utf-8') as out:
        out.write('---\n')
        out.write('deleted: true\n')
        out.write('deleted_by: assistant(model=Codex GPT-5)\n')
        out.write('deleted_at: ' + datetime.now().astimezone().strftime('%Y-%m-%dT%H:%M:%S%z %Z') + '\n')
        out.write('reason: non compliant SPEC_HELPER script\n')
        out.write('original_path: ' + src + '\n')
        out.write('---\n')
        try:
            with open(src,'r',encoding='utf-8') as fin:
                out.write(fin.read())
        except Exception as e:
            out.write(f"<unable to read: {e}>\n")
    os.remove(src)

print('refs:',sorted(refs))
print('noncompliant:',noncompliant)
print('applied:',APPLY)
