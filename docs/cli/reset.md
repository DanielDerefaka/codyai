---
summary: "CLI reference for `codyai reset` (reset local state/config)"
read_when:
  - You want to wipe local state while keeping the CLI installed
  - You want a dry-run of what would be removed
title: "reset"
---

# `codyai reset`

Reset local config/state (keeps the CLI installed).

```bash
codyai backup create
codyai reset
codyai reset --dry-run
codyai reset --scope config+creds+sessions --yes --non-interactive
```

Run `codyai backup create` first if you want a restorable snapshot before removing local state.
