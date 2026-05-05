---
name: session-transcript-extraction
description: Extract đầy đủ + chính xác log/transcript của session Claude Code (kể cả session đã /rename) HOẶC audit session hiện tại trước khi báo cáo tiến độ multi-step. Dùng khi user yêu cầu "lấy transcript", "log session", "lấy lại tiến trình", "audit progress", "status matrix". Output 2 file vào memory dir; KHÔNG summarize, KHÔNG cherry-pick. Verify message count match.
when_to_use: user requests session transcript, log, history, recall a renamed session, continue work cross-session, report progress on multi-step in-flight task (E2E matrix, backlog clear, release cascade)
---

# session-transcript-extraction

## Khi nào dùng

**Use case 1 — Cross-session recall**: User yêu cầu lấy log/transcript của 1 session Claude Code. Keywords trigger:
- "lấy transcript của session X"
- "log của session"
- "history session"
- "lấy lại tiến trình của session"
- "session đã /rename"
- Tên cụ thể của 1 session (vd "cloudflare-pages-deployment-setup")

**Use case 2 — Current-session progress audit (NEW 2026-04-21)**: Trước khi báo cáo status của multi-step in-flight task trong session hiện tại (E2E 24-config matrix, backlog clear N repos, release cascade, multi-PR rollout). Keywords trigger:
- "audit progress" / "audit tiến độ"
- "matrix status" / "còn lại gì" / "đã xong gì"
- Hoặc tự trigger: trước khi render status table / report N/M PASS, luôn audit JSONL trước.

Context-window bias + compaction → recent turns overweight, prior confirmations dropped. Audit = aggregate **full** session history → accurate status.

## Vị trí session JSONL

```
~/.claude/projects/<project-slug>/<session-id>.jsonl
```

Trên Windows: `C:\Users\<user>\.claude\projects\<project-slug>\<session-id>.jsonl`

`<project-slug>` thường là encode của working directory (vd `C--Users-n24q02m-wlap-projects` cho `C:\Users\n24q02m-wlap\projects`).

## Workflow

### 1. Tìm session JSONL

Nếu user gọi tên rename:

```bash
# Search by custom-title hoặc agent-name field
grep -l '"customTitle":"<session-name>"' ~/.claude/projects/<slug>/*.jsonl
# Hoặc
grep -l '"agentName":"<session-name>"' ~/.claude/projects/<slug>/*.jsonl
```

Nếu user nói "session gần nhất":

```bash
ls -lt ~/.claude/projects/<slug>/*.jsonl | head -5
```

Nếu user nói "session về topic X":

```bash
grep -l "<keyword>" ~/.claude/projects/<slug>/*.jsonl
```

### 2. Parse JSONL

Mỗi dòng là 1 JSON event. Các type quan trọng:
- `user` — user message
- `assistant` — assistant response (text + tool_use blocks)
- `system` — system messages, hook events
- `attachment` — tool result attachments
- `file-history-snapshot` — file state snapshots
- `custom-title` — session rename event
- `agent-name` — agent name event

Extract MỌI event `user` + `assistant` theo thứ tự line. KHÔNG lọc tool_use/tool_result/thinking blocks (giữ full context).

### 3. Output 2 file

Save vào memory dir của project: `~/.claude/projects/<slug>/memory/`

```
session-<short-id>-<title>-transcript.md  # full user+assistant content
session-<short-id>-<title>-history.md     # timeline tóm tắt theo line
```

`<short-id>` = first 8 chars của session UUID (vd `571a987b`).

### 4. Verify completeness

```bash
# Total user prompts trong JSONL
grep -c '"type":"user"' <session>.jsonl
# Total assistant trong JSONL
grep -c '"type":"assistant"' <session>.jsonl
# Match với count trong transcript file
```

Nếu count không match → debug parser, KHÔNG ship transcript thiếu.

## Python parser template

```python
import json, base64
from pathlib import Path

src = Path("~/.claude/projects/<slug>/<session-id>.jsonl").expanduser()
out_transcript = Path("~/.claude/projects/<slug>/memory/session-<short>-transcript.md").expanduser()
out_history = Path("~/.claude/projects/<slug>/memory/session-<short>-history.md").expanduser()

events = []
with src.open(encoding='utf-8', errors='replace') as f:
    for i, line in enumerate(f, 1):
        try:
            obj = json.loads(line)
            obj['_line'] = i
            events.append(obj)
        except: pass

def text_from_message(msg):
    if not isinstance(msg, dict): return str(msg)
    content = msg.get('content')
    if isinstance(content, str): return content
    if not isinstance(content, list): return ''
    parts = []
    for block in content:
        if not isinstance(block, dict):
            parts.append(str(block)); continue
        btype = block.get('type')
        if btype == 'text':
            parts.append(block.get('text', ''))
        elif btype == 'thinking':
            t = block.get('thinking', '')
            if t: parts.append(f"[thinking]\n{t}")
        elif btype == 'tool_use':
            name = block.get('name', '')
            inp = json.dumps(block.get('input', {}), ensure_ascii=False)
            if len(inp) > 800: inp = inp[:800] + '...[truncated]'
            parts.append(f"[tool_use: {name}] {inp}")
        elif btype == 'tool_result':
            tid = block.get('tool_use_id', '')
            c = block.get('content')
            if isinstance(c, list):
                c = '\n'.join(x.get('text', str(x)) if isinstance(x, dict) else str(x) for x in c)
            if isinstance(c, str) and len(c) > 600: c = c[:600] + '...[truncated]'
            parts.append(f"[tool_result {tid[:8]}] {c}")
    return '\n'.join(p for p in parts if p)

# Build transcript
msg_count = 0
lines_md = [f'# Session Transcript\n\n**Total raw events**: {len(events)}\n', '\n---\n']
for e in events:
    if e.get('type') not in ('user', 'assistant'): continue
    msg = e.get('message', {})
    role = msg.get('role') if isinstance(msg, dict) else e.get('type')
    body = text_from_message(msg).strip()
    if not body: continue
    msg_count += 1
    lines_md.append(f'\n## {role.upper()} #{msg_count} (line {e["_line"]})\n')
    lines_md.append(body)
    lines_md.append('\n\n---')

out_transcript.parent.mkdir(parents=True, exist_ok=True)
out_transcript.write_text('\n'.join(lines_md), encoding='utf-8')

# Build history (timeline summary)
hist = ['# Session History Timeline\n']
evt_n = 0
for e in events:
    t = e.get('type')
    line = e.get('_line', '?')
    if t == 'user':
        msg = e.get('message', {})
        body = text_from_message(msg).strip()
        if body.startswith('[tool_result'): continue
        evt_n += 1
        snippet = body[:160].replace('\n', ' ')
        hist.append(f'- L{line} **USER #{evt_n}**: {snippet}')
    elif t == 'assistant':
        content = e.get('message', {}).get('content', [])
        if not isinstance(content, list): continue
        for block in content:
            if not isinstance(block, dict): continue
            btype = block.get('type')
            if btype == 'text':
                txt = block.get('text', '').strip()
                if txt:
                    hist.append(f'- L{line} ASSISTANT (text): {txt[:160].replace(chr(10), " ")}')
                    break
            elif btype == 'tool_use':
                name = block.get('name', '')
                inp = block.get('input', {})
                desc = inp.get('description') or inp.get('command') or json.dumps(inp, ensure_ascii=False)
                if isinstance(desc, str): desc = desc[:140].replace('\n', ' ')
                hist.append(f'- L{line} ASSISTANT (tool: {name}): {desc}')
                break
    elif t == 'system':
        st = e.get('subtype', '')
        c = e.get('content', '')
        if isinstance(c, str) and len(c) > 200: c = c[:200] + '...'
        hist.append(f'- L{line} [system:{st}] {c}')
    elif t == 'custom-title':
        hist.append(f'- L{line} [custom-title] {e.get("customTitle")}')

out_history.write_text('\n'.join(hist), encoding='utf-8')
print(f'Transcript: {out_transcript} ({out_transcript.stat().st_size} bytes, {msg_count} msgs)')
print(f'History: {out_history} ({out_history.stat().st_size} bytes)')
```

## Tại sao không summarize

User cần transcript để continue work cross-session sau khi session đã end / compact / cleared. Nếu lọc thiếu → mất context, phải hỏi lại = vi phạm rule "no repeat questions".

Summary là supplementary, KHÔNG thay transcript.

## Use case 2 — Current-session progress audit

### Khi trigger

Bất kỳ status report multi-step nào trong session đang chạy — E2E matrix, backlog clear, release cascade, multi-repo PR rollout. Luôn audit TRƯỚC khi gõ bảng `N/M PASS`.

### Identify current-session JSONL

Session ID không hiện rõ trong context. Cách lock file:

```bash
ls -t ~/.claude/projects/<slug>/*.jsonl | head -3
# File mtime trong vòng vài phút = current session
# Cross-ref: grep "<last_user_msg>" trong file đó nếu cần confirm
```

### Aggregate pattern cho E2E matrix

```bash
PYTHONIOENCODING=utf-8 python -c "
import json, re
JSONL = r'<path/to/current.jsonl>'
events = []
with open(JSONL, encoding='utf-8') as f:
    for i, l in enumerate(f, 1):
        try: events.append((i, json.loads(l)))
        except: pass

# Keywords báo hiệu user confirm PASS
CONFIRM_WORDS = ['ok', 'pass', 'đúng', 'work', 'tiếp', 'được', 'xong']

for idx, (line, e) in enumerate(events):
    if e.get('type') != 'user': continue
    msg = e.get('message', {})
    if not isinstance(msg, dict): continue
    content = msg.get('content')
    body = content if isinstance(content, str) else ''
    if isinstance(content, list):
        body = ' '.join(b.get('text', '') for b in content if isinstance(b, dict) and b.get('type') == 'text')
    low = body.lower().strip()
    if not low or len(low) > 60: continue  # filter out long prompts
    if any(w in low for w in CONFIRM_WORDS):
        # Preceding assistant text = what user is confirming
        for j in range(idx-1, max(0, idx-4), -1):
            _, prev = events[j]
            if prev.get('type') != 'assistant': continue
            c = prev.get('message', {}).get('content', [])
            for b in c if isinstance(c, list) else []:
                if isinstance(b, dict) and b.get('type') == 'text' and b.get('text'):
                    print(f'L{line} USER: {body[:80]}  <-- L{events[j][0]} ASST: {b[\"text\"][:120]}')
                    break
            else: continue
            break
"
```

### Cross-ref output với task list

Build table `<task-id> | JSONL line mention | JSONL line user confirm | status`. PASS chỉ khi có explicit user confirm line. No confirm = PENDING, không fabricate.

### Mention audit trong status report

Status reply phải có dòng đầu kiểu `Audited <N> lines of current-session JSONL (<session-id>.jsonl).` để user biết aggregate thật, không guess.

## Index vào MEMORY.md

Sau khi extract, add 1 dòng vào `~/.claude/projects/<slug>/memory/MEMORY.md` Projects section:

```markdown
- [**Session <name> transcript**](./session-<short>-transcript.md) — N msgs, full log of <name> session
- [**Session <name> history**](./session-<short>-history.md) — timeline of session events
```
