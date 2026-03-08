---
summary: "CLI reference for `codyai config` (get/set/unset/file/validate)"
read_when:
  - You want to read or edit config non-interactively
title: "config"
---

# `codyai config`

Config helpers: get/set/unset/validate values by path and print the active
config file. Run without a subcommand to open
the configure wizard (same as `codyai configure`).

## Examples

```bash
codyai config file
codyai config get browser.executablePath
codyai config set browser.executablePath "/usr/bin/google-chrome"
codyai config set agents.defaults.heartbeat.every "2h"
codyai config set agents.list[0].tools.exec.node "node-id-or-name"
codyai config unset tools.web.search.apiKey
codyai config validate
codyai config validate --json
```

## Paths

Paths use dot or bracket notation:

```bash
codyai config get agents.defaults.workspace
codyai config get agents.list[0].id
```

Use the agent list index to target a specific agent:

```bash
codyai config get agents.list
codyai config set agents.list[1].tools.exec.node "node-id-or-name"
```

## Values

Values are parsed as JSON5 when possible; otherwise they are treated as strings.
Use `--strict-json` to require JSON5 parsing. `--json` remains supported as a legacy alias.

```bash
codyai config set agents.defaults.heartbeat.every "0m"
codyai config set gateway.port 19001 --strict-json
codyai config set channels.whatsapp.groups '["*"]' --strict-json
```

## Subcommands

- `config file`: Print the active config file path (resolved from `CODYAI_CONFIG_PATH` or default location).

Restart the gateway after edits.

## Validate

Validate the current config against the active schema without starting the
gateway.

```bash
codyai config validate
codyai config validate --json
```
