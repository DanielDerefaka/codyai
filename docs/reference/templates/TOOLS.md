# Tools & Integrations

## AI Models Available
| Model | Provider | Use For | API Key |
|-------|----------|---------|---------| 
| Claude Opus 4.6 | Anthropic | Deep reasoning, auditing, complex architecture | ✅ Ready |
| Claude Sonnet 4.5 | Anthropic | Daily operations, code gen, email, content | ✅ Ready |
| GPT-4o-mini | OpenAI | Voice calls, cheap fallback tasks | ✅ Ready |
| GPT-4o | OpenAI | Image understanding, multimodal tasks | ✅ Ready |

## Communication Channels
| Channel | Status | Use |
|---------|--------|-----|
| Telegram | PRIMARY | Main chat with Dx |
| WhatsApp | SECONDARY | Backup, voice notes |
| Discord | MONITOR | Bittensor server |

## APIs & Services
| Service | Status | Purpose |
|---------|--------|---------|
| Twitter/X API | ✅ Ready | Post tweets, read mentions, DMs |
| GitHub Token | ✅ Ready | Repo management, issues, PRs |
| ElevenLabs | ✅ Ready | Voice synthesis for calls |
| Twilio | ✅ Ready | Phone calls to Dx (+2347026986823) |
| Gmail | ✅ Config needed | Email triage |
| Google Calendar | ❌ Not yet | Scheduling |
| Brave Search | Via skill | Web search |

## Payments — Handshake DRAIN Protocol
| Tool | Status | Purpose |
|------|--------|---------|
| drain-mcp | ✅ Ready | Trustless USDC micropayments on Polygon |
| Wallet | ✅ Funded | 0xB3d8B5F624802b2dFc5A1099A94ea93d82c856F5 |

**How to use DRAIN tools:** All DRAIN tools are accessed via `mcporter call drain.<tool_name>`.

Key commands:
- `mcporter call drain.drain_balance` — Check wallet USDC + POL balance
- `mcporter call drain.drain_providers` — List available service providers
- `mcporter call drain.drain_open_channel provider_id=<id> amount=1.0 duration=3600` — Open payment channel
- `mcporter call drain.drain_chat channel_id=<id> messages='[...]'` — Send paid request

See the hs58 skill for full workflow and tool reference.

## Development Tools
- Node.js 22+ on VPS
- npm / pnpm available
- Git configured
- Docker available
- Vercel CLI (install when needed)
- VS Code Server (if needed for remote dev)

## Hosting
- VPS: Already provisioned and running
- CodyAI Gateway: Running on VPS
- Domains: [Ask Dx for any domains he owns]
