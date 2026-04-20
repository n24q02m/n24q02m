---
name: reading-web-exports
description: Extract clean text from web page exports (HTML + accompanying CSS/JS/image folders from "Save As Complete Page", Arena chat exports, browser archives, AI Studio exports). Use khi user share HTML file >500KB hoặc folder có `<name>_files/` style assets. Output text file riêng để Read tool không bị token-limit.
when_to_use: user share large HTML file, "save page as" export, lmarena.ai chat export, AI Studio conversation export, browser archive with CSS/JS/image companion folder
---

# reading-web-exports

## Khi nào dùng

User share:
- File `.html` / `.htm` / `.part` lớn hơn ~200KB (Read tool fail >25k tokens)
- Folder có structure `<page>_files/` chứa CSS + JS + PNG/SVG (browser "Save As Complete")
- Arena chat exports (lmarena.ai): `Arena _ Benchmark & Compare...html`
- AI Studio exports: `.txt` format dài
- Multi-file web research dump

## Nguyên tắc cốt lõi

1. **HTML file chính = nguồn text duy nhất.** Folder đi kèm (`<page>_files/` hoặc folder Drive có CSS/JS/PNG) = **assets để render offline**, KHÔNG phải content riêng. **BỎ QUA** folder trừ khi chứa `.md` / `.txt` / `.json` riêng biệt.
2. **Strip `<script>` + `<style>` trước khi parse.** HTML export thường 70-90% volume là JS bundle + inline CSS → bloat token + noise.
3. **Extract → save to separate `.txt` file** → sau đó dùng `Read` tool với offset/limit bình thường. TUYỆT ĐỐI KHÔNG cố `Read` HTML >1MB trực tiếp (token limit).
4. **UTF-8 encoding bắt buộc** trên Windows: `PYTHONIOENCODING=utf-8` + `sys.stdout.reconfigure(encoding='utf-8')` nếu script dùng `print`. Không có → Vietnamese diacritics crash với `cp1252`.
5. **Deduplicate consecutive lines** + filter `len(line) > 5` → giảm ~30% noise (navigation, repeated menu items).

## Extraction template (Python stdlib only, không cần dep)

```bash
PYTHONIOENCODING=utf-8 python -c "
import sys, re
from html.parser import HTMLParser
sys.stdout.reconfigure(encoding='utf-8')

INPUT = '<path>/page.html'
OUTPUT = '<path>/extracted.txt'

with open(INPUT, 'r', encoding='utf-8', errors='replace') as f:
    content = f.read()

# Strip noise
content = re.sub(r'<script[^>]*>.*?</script>', '', content, flags=re.DOTALL)
content = re.sub(r'<style[^>]*>.*?</style>', '', content, flags=re.DOTALL)

class TextExtract(HTMLParser):
    def __init__(self):
        super().__init__()
        self.text = []
    def handle_data(self, d):
        d = d.strip()
        if d and len(d) > 2:
            self.text.append(d)

p = TextExtract()
p.feed(content)
lines = '\n'.join(p.text).split('\n')

# Dedupe while preserving order
seen = set()
out = [l for l in lines if len(l) > 5 and not (l in seen or seen.add(l))]

with open(OUTPUT, 'w', encoding='utf-8') as f:
    f.write('\n'.join(out))

print(f'Total: {len(lines)} lines → Unique meaningful: {len(out)} lines')
print(f'Saved: {OUTPUT}')
"
```

Sau đó: `Read OUTPUT limit=400` từng batch để nạp vào context.

## Folder có nhiều HTML (multi-page export)

Arena chat exports thường dump nhiều file: `Arena _ Benchmark 1.html`, `Arena _ Benchmark 2.html`, v.v. Mỗi file = 1 conversation session khác nhau. Strategy:

1. `ls -la *.html` + check file size → file lớn hơn có content giàu hơn.
2. Extract từng file riêng → save `extracted_<n>.txt`.
3. Đọc overview (top 50 lines) của mỗi file → user queries chỉ nhắm file liên quan.
4. Nếu tất cả cùng topic → concatenate rồi dedupe toàn bộ: `cat extracted_*.txt | awk '!seen[$0]++' > merged.txt`.

## GDrive workflow (khi user share link)

Xem memory `feedback_gdrive_rclone.md`. Tóm tắt:
1. Thử ổ `G:/My Drive/` trước (đã sync sẵn).
2. `gdown <file_id>` cho file, `gdown --folder --remaining-ok <folder_url>` cho folder (>50 files cần flag).
3. `rclone backend copyid gdrive: <id> <path>` nếu gdown fail.
4. Local Windows, KHÔNG SSH VM.

Folder ID lấy từ URL dạng `https://drive.google.com/drive/folders/<ID>`. File ID từ `https://drive.google.com/file/d/<ID>/view`.

## Anti-patterns

- **Đọc HTML thô bằng Read tool khi >1MB** → sẽ fail "token limit exceeded", tốn 1 round-trip.
- **Cat HTML với `grep -oE '<p>...'`** → miss multi-line tags, miss nested structure, miss entities chưa decode.
- **Tải hàng trăm CSS/JS từ folder companion** → tốn time, zero content value. Skip folder hoặc chỉ lấy `.md`/`.txt`/`.json` nếu có.
- **Dùng BeautifulSoup/lxml** → cần install thêm, stdlib `html.parser` đủ dùng cho extract plain text.
- **Print trực tiếp ra terminal Windows không `PYTHONIOENCODING=utf-8`** → crash UnicodeEncodeError với Vietnamese/emoji.
- **KHÔNG dedupe** → output 2-3× bloat do navigation repeated mỗi section.

## Khi extraction kém chất lượng

Nếu output .txt trông lộn xộn (mất thứ tự, quá nhiều 1-word lines):
1. HTML dùng heavy client-side rendering (React SPA) → text ở `<script id="__NEXT_DATA__">` hoặc tương tự. Regex extract JSON blob rồi `json.loads`.
2. Content bị obfuscate/encrypted → không extract được, báo user + suggest alternative (ask user to copy-paste content trực tiếp).
3. File là binary (zip/pdf disguised as html) → `file <path>` check MIME, handle theo type thật.
