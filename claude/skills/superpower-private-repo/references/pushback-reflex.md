# Pushback Reflex — STOP + RE-AUDIT (no continue trajectory)

## Trigger signals

User message contains: '???', '!!!', '???!!!', 'đã nói rồi', 'bao lần làm thế rồi', 'lần thứ N', 'không thấy hả?', 'làm cảnh hả?', 'không có 1 chút thinking nào sao?', 'cứ cắm đầu làm vậy?', 'không tự biết đường mà re-thinking re-audit?', 'again wrong'. OR user gửi cùng câu 2 lần liên tiếp.

## Reflex sequence (BẮT BUỘC, NO skip step)

1. **STOP execution** — kill bg task, cancel monitor
2. **Invoke skill `session-transcript-extraction`** → ACTUALLY OPEN + READ 2 file output (không chỉ extract)
3. **Read spec + plan** đang execute
4. **Grep MEMORY.md** + read relevant `feedback_*.md`
5. **Response opening BẮT BUỘC**: "Em đã đọc lại transcript L1-L<latest>, spec X, plan Y, memory Z" + concrete state report (cite line + commit SHA + file:line)
6. **Apply rule mới phát hiện** vào next action — không save memory rồi tiếp tục pattern cũ

## Anti-patterns CẤM

- Response "Em đang chờ anh chọn (a/b/c)" sau pushback
- Extract transcript file qua tool nhưng không đọc
- Lặp lại same explanation rephrase

## Violation context

525c9518 USER #47/48/49/50 (4 lần liên tiếp pushback re-audit, em không reflex).

Memory: `feedback_pushback_reaudit_reflex.md`.
