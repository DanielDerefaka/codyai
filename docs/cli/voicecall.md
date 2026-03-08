---
summary: "CLI reference for `codyai voicecall` (voice-call plugin command surface)"
read_when:
  - You use the voice-call plugin and want the CLI entry points
  - You want quick examples for `voicecall call|continue|status|tail|expose`
title: "voicecall"
---

# `codyai voicecall`

`voicecall` is a plugin-provided command. It only appears if the voice-call plugin is installed and enabled.

Primary doc:

- Voice-call plugin: [Voice Call](/plugins/voice-call)

## Common commands

```bash
codyai voicecall status --call-id <id>
codyai voicecall call --to "+15555550123" --message "Hello" --mode notify
codyai voicecall continue --call-id <id> --message "Any questions?"
codyai voicecall end --call-id <id>
```

## Exposing webhooks (Tailscale)

```bash
codyai voicecall expose --mode serve
codyai voicecall expose --mode funnel
codyai voicecall expose --mode off
```

Security note: only expose the webhook endpoint to networks you trust. Prefer Tailscale Serve over Funnel when possible.
