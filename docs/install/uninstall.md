---
summary: "Uninstall CodyAI completely (CLI, service, state, workspace)"
read_when:
  - You want to remove CodyAI from a machine
  - The gateway service is still running after uninstall
title: "Uninstall"
---

# Uninstall

Two paths:

- **Easy path** if `codyai` is still installed.
- **Manual service removal** if the CLI is gone but the service is still running.

## Easy path (CLI still installed)

Recommended: use the built-in uninstaller:

```bash
codyai uninstall
```

Non-interactive (automation / npx):

```bash
codyai uninstall --all --yes --non-interactive
npx -y codyai uninstall --all --yes --non-interactive
```

Manual steps (same result):

1. Stop the gateway service:

```bash
codyai gateway stop
```

2. Uninstall the gateway service (launchd/systemd/schtasks):

```bash
codyai gateway uninstall
```

3. Delete state + config:

```bash
rm -rf "${CODYAI_STATE_DIR:-$HOME/.codyai}"
```

If you set `CODYAI_CONFIG_PATH` to a custom location outside the state dir, delete that file too.

4. Delete your workspace (optional, removes agent files):

```bash
rm -rf ~/.codyai/workspace
```

5. Remove the CLI install (pick the one you used):

```bash
npm rm -g codyai
pnpm remove -g codyai
bun remove -g codyai
```

6. If you installed the macOS app:

```bash
rm -rf /Applications/CodyAI.app
```

Notes:

- If you used profiles (`--profile` / `CODYAI_PROFILE`), repeat step 3 for each state dir (defaults are `~/.codyai-<profile>`).
- In remote mode, the state dir lives on the **gateway host**, so run steps 1-4 there too.

## Manual service removal (CLI not installed)

Use this if the gateway service keeps running but `codyai` is missing.

### macOS (launchd)

Default label is `ai.codyai.gateway` (or `ai.codyai.<profile>`; legacy `com.codyai.*` may still exist):

```bash
launchctl bootout gui/$UID/ai.codyai.gateway
rm -f ~/Library/LaunchAgents/ai.codyai.gateway.plist
```

If you used a profile, replace the label and plist name with `ai.codyai.<profile>`. Remove any legacy `com.codyai.*` plists if present.

### Linux (systemd user unit)

Default unit name is `codyai-gateway.service` (or `codyai-gateway-<profile>.service`):

```bash
systemctl --user disable --now codyai-gateway.service
rm -f ~/.config/systemd/user/codyai-gateway.service
systemctl --user daemon-reload
```

### Windows (Scheduled Task)

Default task name is `CodyAI Gateway` (or `CodyAI Gateway (<profile>)`).
The task script lives under your state dir.

```powershell
schtasks /Delete /F /TN "CodyAI Gateway"
Remove-Item -Force "$env:USERPROFILE\.codyai\gateway.cmd"
```

If you used a profile, delete the matching task name and `~\.codyai-<profile>\gateway.cmd`.

## Normal install vs source checkout

### Normal install (install.sh / npm / pnpm / bun)

If you used `https://codyai.ai/install.sh` or `install.ps1`, the CLI was installed with `npm install -g codyai@latest`.
Remove it with `npm rm -g codyai` (or `pnpm remove -g` / `bun remove -g` if you installed that way).

### Source checkout (git clone)

If you run from a repo checkout (`git clone` + `codyai ...` / `bun run codyai ...`):

1. Uninstall the gateway service **before** deleting the repo (use the easy path above or manual service removal).
2. Delete the repo directory.
3. Remove state + workspace as shown above.
