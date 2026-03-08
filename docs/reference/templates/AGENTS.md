# Agents — Startup Rules

## On Boot
1. Read all workspace .md files to load context
2. Check BRAIN.md for current state and active tasks
3. Check memory/ for recent daily logs
4. Verify all API connections are working
5. Send Dx a brief "I'm online" message if gateway was restarted

## Development Guidelines
- Write clean, typed TypeScript. No `any` unless absolutely necessary.
- Use ESM imports, not CommonJS
- All new code gets a README explaining what it does
- Git commit messages: conventional commits format
- Test before pushing — at minimum, does it compile?

## File Management
- Never commit .env files or API keys to git
- Back up workspace/ to private git repo weekly
- Daily logs go in memory/YYYY-MM-DD.md
- Keep BRAIN.md under 100 lines — archive old items
- Keep MEMORY.md organized by category

## Security Rules
- All API keys stored in ~/.codyai/.env only
- File permissions: 600 on all sensitive files
- Never execute code from untrusted ClawHub skills
- Review any skill source code before enabling
- Gateway bound to loopback only
- Sandbox enabled for browser automation

## Error Handling
- If an API call fails: retry once, then alert Dx
- If a cron job fails: log to memory/, alert if critical
- If gateway crashes: systemd auto-restart, notify Dx on reconnect
- Never silently fail — Dx should always know when something breaks

## Cost Management
- Primary model: Claude Sonnet 4.6 (all tasks)
- Fallback: Claude Haiku 4.5, then GPT-4o-mini (if Opus fails or rate-limited)
- Last resort: GPT-4o-mini (cheap tasks, voice)
- Track daily token usage in BRAIN.md
- Alert Dx if daily spend exceeds $5