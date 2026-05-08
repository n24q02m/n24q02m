# Virtual Company Config (17/04 pivot v4)

Sync từ infra-vnic — config cho Paperclip VC sau pivot sang Hermes Agent + Gemini 3 Flash Preview.

## Files

| File | Deploy path | Purpose |
|------|-------------|---------|
| `hermes-SOUL.md` | `/home/ubuntu/.hermes/SOUL.md` | Hermes persona: VC Secretary identity + DB schema + scripts context |
| `priority-scheduler.sh` | `/home/ubuntu/virtual-company/scripts/priority-scheduler.sh` | 4-wake weekday + 1-wake weekend scheduler (replaces project-rotator.sh) |
| `test_priority_scheduler.sh` | `/home/ubuntu/virtual-company/tests/scripts/test_priority_scheduler.sh` | TDD 7/7 tests for priority-scheduler |

## Pivot log

**Từ 23/03 → 17/04**: architecture sai. `relay.py` (standalone Python) polling vc_control_bot, trực tiếp UPDATE Paperclip DB. Claude secretary screen riêng biệt, plugin:telegram crashed (missing `.env`).

**Sau 17/04 pivot v4**: Hermes Agent v0.10.0 thay thế cả 2. Systemd user service `hermes-gateway.service` poll vc_control_bot, dùng Gemini 3 Flash Preview với SOUL.md load toàn bộ Paperclip context, có shell tool access → query/update DB + chạy scripts.

## Deploy (trên infra-vnic)

```bash
# SOUL.md
scp hermes-SOUL.md ubuntu@infra-vnic:/home/ubuntu/.hermes/SOUL.md
tailscale ssh ubuntu@infra-vnic 'chmod 600 /home/ubuntu/.hermes/SOUL.md'

# priority-scheduler.sh + tests
scp priority-scheduler.sh ubuntu@infra-vnic:/home/ubuntu/virtual-company/scripts/
scp test_priority_scheduler.sh ubuntu@infra-vnic:/home/ubuntu/virtual-company/tests/scripts/
tailscale ssh ubuntu@infra-vnic 'chmod +x /home/ubuntu/virtual-company/scripts/priority-scheduler.sh /home/ubuntu/virtual-company/tests/scripts/test_priority_scheduler.sh'

# Hermes gateway systemd
tailscale ssh ubuntu@infra-vnic 'hermes gateway install && hermes gateway start'

# Verify
tailscale ssh ubuntu@infra-vnic 'hermes gateway status'
tailscale ssh ubuntu@infra-vnic 'bash /home/ubuntu/virtual-company/tests/scripts/test_priority_scheduler.sh'
```

## Secrets required in `/home/ubuntu/.hermes/.env`

```
GOOGLE_API_KEY=<AI Studio key>
GEMINI_API_KEY=<same key>
TELEGRAM_BOT_TOKEN=<vc_control_bot token from VC_TELEGRAM_BOT_TOKEN in .env.relay>
TELEGRAM_ALLOWED_USERS=7305908576
TELEGRAM_HOME_CHANNEL=7305908576
TELEGRAM_HOME_CHANNEL_NAME=N24Q02M-VC
```

chmod 600.
