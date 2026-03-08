---
summary: "CLI reference for `codyai uninstall` (remove gateway service + local data)"
read_when:
  - You want to remove the gateway service and/or local state
  - You want a dry-run first
title: "uninstall"
---

# `codyai uninstall`

Uninstall the gateway service + local data (CLI remains).

```bash
codyai backup create
codyai uninstall
codyai uninstall --all --yes
codyai uninstall --dry-run
```

Run `codyai backup create` first if you want a restorable snapshot before removing state or workspaces.
