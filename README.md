# CodyAI - AI Co-Pilot with Bittensor Intelligence

CodyAI is a multi-channel AI co-pilot with built-in Bittensor subnet research capabilities. Forked from [OpenClaw](https://github.com/openclaw/openclaw) (MIT), CodyAI comes pre-configured with:

- Bittensor subnet intelligence pipeline (Taostats API + Desearch + GitHub analysis)
- Multi-channel messaging (Telegram, Discord, WhatsApp, Slack, and more)
- X/Twitter content creation with proven engagement frameworks
- Discord read-only server monitoring
- Voice calls, email triage, and cron-based automation

## Quick Start

### Prerequisites
- Node.js 22.12+
- pnpm

### Install

```bash
# Clone the repo
git clone https://github.com/DanielDerefaka/codyai.git
cd codyai

# Install dependencies
pnpm install

# Build
pnpm build

# Run onboarding
node codyai.mjs
```

### Configure

```bash
# Copy environment template
cp .env.example ~/.codyai/.env

# Edit with your API keys (at minimum, set ANTHROPIC_API_KEY)
nano ~/.codyai/.env
```

### Required API Keys

| Key | Source | Purpose |
|-----|--------|---------|
| `ANTHROPIC_API_KEY` | [console.anthropic.com](https://console.anthropic.com) | AI model (Claude) |
| `TAOSTATS_API_KEY` | [dash.taostats.io](https://dash.taostats.io) | Bittensor on-chain data |
| `DESEARCH_API_KEY` | [console.desearch.ai](https://console.desearch.ai) | X/Twitter sentiment + web search |

Optional: `TELEGRAM_BOT_TOKEN`, `DISCORD_BOT_TOKEN`, `DISCORD_USER_TOKEN`, `X_BEARER_TOKEN`, `ELEVENLABS_API_KEY`

## Built-in Skills

### Bittensor Research (`/bittensor-research`)

Pulls live data from multiple sources and generates comprehensive subnet intelligence reports:

```bash
# Full subnet report
python3 scripts/subnet-research.py report <netuid>

# Scan all subnets
python3 scripts/subnet-research.py scan

# Top profitable subnets
python3 scripts/subnet-research.py top <N>
```

**Data sources:** Taostats API (on-chain data, metagraph, emissions), Desearch API (X/Twitter sentiment, web search), GitHub API (repo activity, README analysis)

### Content Writing (`/content-writing`)

X/Twitter post drafting using proven engagement frameworks. Supports long-form posts (1500-3500 chars) with tension loops, micro-stories, and cross-domain synthesis.

## Architecture

CodyAI is built on OpenClaw's multi-channel gateway architecture:

- **Gateway:** Local HTTP server (loopback-bound) handling all messaging channels
- **Channels:** Telegram, Discord, WhatsApp, Slack, Signal, iMessage, Matrix, MS Teams, and more
- **Skills:** Extensible skill system via markdown SKILL.md files
- **Memory:** Daily logs, persistent BRAIN.md, long-term MEMORY.md
- **Cron:** Scheduled tasks (morning briefings, evening summaries, health checks)
- **LLM:** Multi-provider support (Anthropic primary, OpenAI/Gemini fallback)

## Customization

### Personality
Edit `~/.codyai/workspace/SOUL.md` to customize Cody's personality, responsibilities, and behavior.

### Skills
Add new skills in `~/.codyai/skills/<skill-name>/SKILL.md` with YAML frontmatter.

### Reference Files
Add domain knowledge in `~/.codyai/workspace/reference/` (loaded on-demand by skills).

## Development

```bash
pnpm install          # Install deps
pnpm build            # Build TypeScript
pnpm test             # Run tests
pnpm check            # Lint + format check
pnpm dev              # Run in dev mode
```

## Credits

CodyAI is a fork of [OpenClaw](https://github.com/openclaw/openclaw) by the OpenClaw team. Licensed under MIT.

Built by [@DanielDerefaka](https://github.com/DanielDerefaka)
