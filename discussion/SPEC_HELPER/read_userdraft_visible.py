#!/usr/bin/env python3
import sys, re
from pathlib import Path
p=Path('discussion/UserDraft.md')
if not p.exists():
    sys.exit(0)
text=p.read_text(encoding='utf-8', errors='ignore').splitlines()
# find last divider: line that is only --- (allow whitespace)
last=-1
for i,ln in enumerate(text):
    if re.match(r'^\s*---\s*$', ln):
        last=i
if last==-1:
    # no divider => nothing visible
    sys.exit(0)
visible='\n'.join(text[last+1:])
print(visible)
