#!/usr/bin/env python3
import re, sys, os
from datetime import datetime

SRC='discussion/ChatHistory.md'
OUT='discussion/ChatIndex.md'

lines=open(SRC,'r',encoding='utf-8').read().splitlines()
start_re=re.compile(r'^(?P<fence>`{3,})(?:\s*md)?\s*\{(?P<attrs>[^}]*)\}\s*$')
end_re=lambda n: re.compile(r'^`{%d}\s*$'%n)
kv_re=re.compile(r'(\w+)\s*=\s*"([^"]*)"|(\w+)\s*=\s*([^\s\}]+)')

def parse_attrs(s):
    d={}
    for m in kv_re.finditer(s):
        if m.group(1): d[m.group(1)]=m.group(2)
        else: d[m.group(3)]=m.group(4)
    return d

blocks=[]; i=0; n=len(lines)
while i<n:
    m=start_re.match(lines[i])
    if not m: i+=1; continue
    fence=m.group('fence'); fl=len(fence); attrs_raw=m.group('attrs'); attrs=parse_attrs(attrs_raw); i0=i
    i+=1; body=[]; er=end_re(fl)
    while i<n and not er.match(lines[i]): body.append(lines[i]); i+=1
    if i<n: i+=1
    blocks.append({'line':i0+1,'attrs':attrs,'body':'\n'.join(body)})

# helper: parse ts
from datetime import datetime

def parse_ts(s):
    try: return datetime.strptime(s,'%Y-%m-%dT%H:%M:%S%z %Z')
    except: return None

# topic key = situation or '(no-situation)'
from collections import defaultdict

TOPIC_TITLES={
  "chathistory-format": ("ChatHistory 格式设计", "fenced 结构与代码块属性、格式迁移等"),
  "fencing-escalation": ("外层 Fence 加长规则", "正文含反引号时外层 fence 长度 m+1"),
  "trash-policy": (".trush 策略与命名", "入库/frontmatter/时间戳命名规范"),
  "intent-structure": ("Intent 三段式结构", "事实/推断/建议"),
  "record-policy-no-record": ("No-Record 原则", "低信息量对话不入档与固定告知"),
  "timestamp-format": ("时间戳与本地时区", "ISO8601+偏移+缩写"),
  "validation-report": ("校验报告与临时产物", "验证产物与目录纯净"),
  "spec-update-policy": ("规范更新与策略", "角色特定记录与裁剪"),
  "module-spec_tool_and-chatindex_structured_indexing": ("模块工具与 ChatIndex", "每模块 SPEC_TOOL 与结构化话题索引"),
  "spec-recording_rules-attrs_ts_situation-user_heavy-assistant_strict": ("记录规则与格式", "使用 ts+situation；用户多记录/助理严格控制"),
  "scan-annotate_situations_and-missing_log_inquiry": ("补标与遗漏入档排查", "自动补 situation 与缺失记录排查"),
  "spec_tooling-situation_annotator": ("SPEC 工具：补标脚本", "annotate_situations.py 的创建与执行"),
  "general-discussion": ("通用讨论", "尚未分类的对话"),
}

grp=defaultdict(list)
for b in blocks:
    sit=b['attrs'].get('situation') or '(no-situation)'
    grp[sit].append(b)

# sort blocks in each group by ts then line
for k in grp:
    grp[k].sort(key=lambda b: (parse_ts(b['attrs'].get('ts','')) or datetime.min.replace(tzinfo=None), b['line']))

# write structured index
with open(OUT,'w',encoding='utf-8') as f:
    f.write('# Chat Index\n\n')
    f.write('- source: %s\n' % SRC)
    f.write('- generated_at: %s\n' % datetime.now().astimezone().strftime('%Y-%m-%dT%H:%M:%S%z %Z'))
    f.write('- note: 如无特殊强调，以下所有行号均指向上方 source 文件\n\n')
    for sit in sorted(grp.keys()):
        blocks=grp[sit]
        if not blocks: continue
        ts_list=[b['attrs'].get('ts','') for b in blocks if b['attrs'].get('ts')]
        start_ts=ts_list[0] if ts_list else 'unknown'
        end_ts=ts_list[-1] if ts_list else 'unknown'
        # compute line range (min..max)
        min_line=min(b['line'] for b in blocks)
        max_line=max(b['line'] for b in blocks)
        title,desc = TOPIC_TITLES.get(sit,(sit,'(未定义主题描述)'))
        f.write('## %s (key: %s)\n' % (title, sit))
        f.write('- desc: %s\n' % desc)
        f.write('- span_ts: %s ~ %s\n' % (start_ts, end_ts))
        f.write('- span_lines: %d..%d\n' % (min_line, max_line))
        # summarize entries minimally: mark role
        for b in blocks:
            role='assistant' if (b['attrs'].get('by','')=='assistant' or str(b['attrs'].get('cr','')).startswith('assistant')) else 'user'
            preview=b['body'].splitlines()[0].strip() if b['body'] else ''
            if len(preview)>80: preview=preview[:77]+'...'
            f.write('  - %s: L%d %s\n' % (role, b['line'], preview))
        f.write('\n')
print('wrote', OUT)
