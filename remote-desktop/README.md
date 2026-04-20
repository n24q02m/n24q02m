# Self-hosted Remote Desktop with RustDesk + Tailscale

Full GUI remote desktop between multiple machines using self-hosted RustDesk server on a VPS, connected through Tailscale mesh VPN. No ports exposed to the internet.

## Architecture

```
Machine A ──Tailscale──> VPS (RustDesk Server) <──Tailscale── Machine B
  100.x.x.x              100.x.x.x:21116                     100.x.x.x
                          hbbs + hbbr (Docker)
```

**Why this stack:**

| Layer | Role |
|-------|------|
| **Tailscale** | Mesh VPN (WireGuard-based). Machines see each other via `100.x.x.x` IPs. No port forwarding, no dynamic DNS. Free for personal use. |
| **RustDesk Server** | Self-hosted ID/relay server. Clients register with hbbs, relay through hbbr when direct P2P fails. Runs in Docker (~128MB total). |
| **RustDesk Client** | Cross-platform (Windows/Linux/macOS). Peer-to-peer with E2E encryption (NaCl). Unattended access with permanent password. |

**Why not Cloudflare Tunnel:** RustDesk native client connects directly to TCP port 21116. CF Tunnel only exposes HTTPS port 443. The client cannot route its TCP protocol through HTTPS -- this is an architectural mismatch, not a config issue. WebSocket mode exists but only works in-browser, not with the native client for reliable desktop access.

## Prerequisites

- A VPS with Docker (the RustDesk server, e.g. OCI free tier ARM64)
- [Tailscale](https://tailscale.com) account (free, up to 100 devices)
- [RustDesk](https://rustdesk.com) client on each machine

## Step 1: Deploy RustDesk Server on VPS

### 1.1 Install Tailscale on VPS

```bash
curl -fsSL https://tailscale.com/install.sh | sh
sudo tailscale up
# Open the URL in browser to authenticate
```

Note the Tailscale IP (e.g. `<VPS_TAILSCALE_IP>`, a `100.x.y.z` address).

### 1.2 Deploy RustDesk Server

**docker-compose.yml:**

```yaml
services:
  rustdesk-hbbs:
    image: rustdesk/rustdesk-server:latest
    container_name: rustdesk-hbbs
    command: hbbs
    restart: unless-stopped
    ports:
      - "21115:21115"
      - "21116:21116"
      - "21116:21116/udp"
    volumes:
      - rustdesk-data:/root
    depends_on:
      - rustdesk-hbbr
    deploy:
      resources:
        limits:
          memory: 64M

  rustdesk-hbbr:
    image: rustdesk/rustdesk-server:latest
    container_name: rustdesk-hbbr
    command: hbbr
    restart: unless-stopped
    ports:
      - "21117:21117"
    volumes:
      - rustdesk-data:/root
    deploy:
      resources:
        limits:
          memory: 64M

volumes:
  rustdesk-data:
```

```bash
docker compose up -d
```

### 1.3 Get the Public Key

```bash
docker logs rustdesk-hbbs 2>&1 | grep "Key:"
# Output: Key: <YOUR_PUBLIC_KEY>
```

Save this key -- every client needs it.

### 1.4 Security

Ports 21115-21117 are bound to `0.0.0.0` on the host but **only reachable via Tailscale** because:
- Cloud firewall (e.g. OCI Security List) blocks all inbound except SSH
- OS firewall (iptables) has a default REJECT rule
- Tailscale traffic bypasses both firewalls via the `tailscale0` interface

**Do NOT open these ports in your cloud firewall.**

## Step 2: Add a New Machine

### 2.1 Install Tailscale

**Windows:**
```
winget install Tailscale.Tailscale
```

**Ubuntu/Debian:**
```bash
curl -fsSL https://tailscale.com/install.sh | sh
sudo tailscale up
```

**macOS:**
```
brew install tailscale
```

Authenticate with the same Tailscale account as the VPS. Verify:

```bash
tailscale status
# Should see the VPS and all other machines
```

### 2.2 Install RustDesk Client

Download from [rustdesk.com](https://rustdesk.com/download) or:

**Windows:**
```
winget install RustDesk.RustDesk
```

**Ubuntu/Debian:**
```bash
# Check latest version at https://github.com/rustdesk/rustdesk/releases
wget https://github.com/rustdesk/rustdesk/releases/download/<VERSION>/rustdesk-<VERSION>-x86_64.deb
sudo apt install -y ./rustdesk-*.deb
```

### 2.3 Configure RustDesk Client

Open RustDesk GUI > **Settings** > **Network** > **ID/Relay server**:

| Field | Value |
|-------|-------|
| ID Server | `<VPS_TAILSCALE_IP>` (a `100.x.y.z` Tailscale address) |
| Relay Server | `<VPS_TAILSCALE_IP>` |
| API Server | (leave empty) |
| Key | `<YOUR_PUBLIC_KEY>` from Step 1.3 |

**Important:** Do NOT enable "Use WebSocket". Use TCP (default).

### 2.4 Set Permanent Password

For unattended access, set a permanent password:

**Via GUI:** Settings > Security > Permanent Password

**Via CLI (Linux, requires sudo):**
```bash
sudo rustdesk --password <YOUR_PASSWORD>
```

**Via config file (Windows):**
1. Close RustDesk
2. Edit `%APPDATA%\RustDesk\config\RustDesk.toml`
3. Set `password = '<YOUR_PASSWORD>'` (plain text)
4. Start RustDesk -- it will auto-encrypt the password

### 2.5 Enable Auto-start

**Windows:** RustDesk auto-starts by default. Or add to registry:
```powershell
New-ItemProperty -Path 'HKCU:\SOFTWARE\Microsoft\Windows\CurrentVersion\Run' -Name 'RustDesk' -Value '"<RUSTDESK_PATH>\rustdesk.exe" --tray'
```

**Ubuntu:**
```bash
sudo systemctl enable rustdesk
sudo systemctl start rustdesk
```

### 2.6 Verify Connection

RustDesk main screen should show **"Ready"** (green dot). If it shows "Connecting..." or "Not Ready":

1. Check Tailscale: `tailscale ping <VPS_TAILSCALE_IP>`
2. Check port: `nc -zv <VPS_TAILSCALE_IP> 21116`
3. Restart RustDesk

### 2.7 Record Machine Info

Note down for your records:

| Info | Value |
|------|-------|
| Machine name | |
| RustDesk ID | (shown on main screen) |
| Permanent password | |
| Tailscale IP | `tailscale ip -4` |
| OS | |

## Step 3: Connect Between Machines

1. Open RustDesk on Machine A
2. Enter the **RustDesk ID** of Machine B
3. Enter Machine B's **permanent password**
4. Full GUI remote desktop

**Tips:**
- Lock the remote machine when disconnecting (Ctrl+Alt+L on Linux, Win+L on Windows)
- Enable "Lock session on disconnect" in RustDesk Settings > Security
- RustDesk traffic goes P2P through Tailscale when possible (~40ms), or relays through the VPS

## Troubleshooting

| Issue | Solution |
|-------|----------|
| "Not Ready" | Check Tailscale is connected: `tailscale status` |
| "Connecting..." forever | Verify VPS Tailscale IP in RustDesk settings, check firewall |
| Config gets reset (Linux) | RustDesk service (root) overwrites user config. Set via GUI, not file edit |
| Password not accepted | Re-set password via GUI (Settings > Security), restart RustDesk |
| High latency | Check `tailscale ping` -- DERP relay adds ~40ms, direct P2P is faster |
| Can't install on Windows remotely | MSI/EXE needs admin elevation GUI. Install when physically at the machine |
