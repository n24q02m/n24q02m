# Internet Tunnel: VDI to Physical Machine

Setup để VDI trong mạng nội bộ (bị Fortinet SSL inspection + domain filter) có thể truy cập internet qua máy vật lý, dùng cho các tool cần search web (Claude Code MCP, curl, v.v.).

## Bối cảnh

```
VDI (Ubuntu 20, 10.8.68.x)
  - Fortinet firewall chặn: SSH outbound (port 22), HTTP (port 80)
  - Fortinet SSL inspection: MITM toàn bộ HTTPS, inject cert Fortinet
  - Chỉ mở: HTTPS outbound (port 443)
  - Hậu quả: Tailscale không dùng được (pin cert, bị reject)

Máy vật lý (Ubuntu 22, 10.1.45.x)
  - Kết nối vào VDI qua Omnissa Horizon (display only, không có network route)
  - Có Tailscale (100.89.181.x) nhưng VDI không reach được
  - Có internet bình thường
```

## Giải pháp: chisel + Cloudflare Tunnel

```
VDI ──[WebSocket/443]──> Cloudflare ──> Máy vật lý (cloudflared + chisel)
                                                  |
                                            Internet
```

**Tại sao chisel qua Cloudflare:**
- Port 443 là port duy nhất mở outbound từ VDI
- Cloudflare Tunnel (trycloudflare.com) dùng HTTPS/WebSocket, Fortinet không block
- chisel dùng WebSocket, không pin cert → không bị Fortinet reject
- Không cần server riêng, không cần IP public

## Setup

### Yêu cầu

- `chisel` binary trên cả 2 máy
- `cloudflared` binary trên máy vật lý (VDI đã có sẵn tại `~/.local/bin/cloudflared`)

### Cài chisel

**Máy vật lý:**
```bash
CHISEL_VER=$(curl -s https://api.github.com/repos/jpillora/chisel/releases/latest | grep '"tag_name"' | cut -d'"' -f4 | tr -d 'v')
curl -L "https://github.com/jpillora/chisel/releases/download/v${CHISEL_VER}/chisel_${CHISEL_VER}_linux_amd64.gz" -o chisel.gz
gunzip chisel.gz && chmod +x chisel
mv chisel ~/chisel
```

**VDI:**
```bash
CHISEL_VER=1.11.5  # hoặc version mới nhất
curl -L "https://github.com/jpillora/chisel/releases/download/v${CHISEL_VER}/chisel_${CHISEL_VER}_linux_amd64.gz" -o /tmp/chisel.gz
gunzip /tmp/chisel.gz && chmod +x /tmp/chisel
```

### Cài cloudflared (máy vật lý nếu chưa có)

```bash
curl -L https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64 -o ~/cloudflared
chmod +x ~/cloudflared
```

## Sử dụng hàng ngày

### Bước 1 — Máy vật lý: terminal 1

```bash
~/chisel server --port 8080 --socks5
```

### Bước 2 — Máy vật lý: terminal 2

```bash
~/cloudflared tunnel --url http://localhost:8080
```

Chờ xuất hiện URL dạng:
```
https://xxxx-yyyy-zzzz.trycloudflare.com
```

### Bước 3 — VDI: kết nối và tạo SOCKS5 proxy

```bash
/tmp/chisel client --keepalive 10s https://xxxx-yyyy-zzzz.trycloudflare.com socks &
```

Nếu thành công sẽ thấy:
```
client: tun: proxy#127.0.0.1:1080=>socks: Listening
client: Connected (Latency ~50ms)
```

### Bước 4 — VDI: set proxy

```bash
export http_proxy="socks5://127.0.0.1:1080"
export https_proxy="socks5://127.0.0.1:1080"
export all_proxy="socks5://127.0.0.1:1080"
```

Test:
```bash
curl --socks5-hostname 127.0.0.1:1080 https://ifconfig.me
# → IP của máy vật lý
```

## Lưu ý

- **URL thay đổi mỗi lần** restart cloudflared (free tier). Cần copy URL mới và chạy lại chisel client.
- **Không Ctrl+C** cloudflared hay chisel server khi VDI đang dùng.
- chisel binary ở `/tmp/` sẽ mất sau khi reboot VDI — cần tải lại hoặc lưu vào `~/.local/bin/`.
- MCP server (wet-mcp) chạy process riêng, không nhận env var proxy từ shell — cần tìm cách config riêng nếu muốn MCP dùng proxy.

## Tại sao các phương án khác không dùng được

| Phương án | Lý do không dùng được |
|-----------|----------------------|
| Tailscale trực tiếp | Fortinet SSL inspection reject cert của `controlplane.tailscale.com` (pin cert) |
| SSH tunnel (-D SOCKS5) | Port 22 outbound bị block |
| SSH over 443 (cloudflared access tcp) | Cần WebSocket handshake, SSH dùng TCP thuần → bad handshake |
| chisel từ VDI đến máy vật lý trực tiếp | VDI (10.8.68.x) và máy vật lý (10.1.45.x) khác subnet, không có route |
| Tailscale trên VDI | Binary có sẵn nhưng daemon không thể kết nối control plane do Fortinet MITM |
