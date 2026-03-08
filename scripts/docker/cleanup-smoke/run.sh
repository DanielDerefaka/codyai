#!/usr/bin/env bash
set -euo pipefail

cd /repo

export CODYAI_STATE_DIR="/tmp/openclaw-test"
export CODYAI_CONFIG_PATH="${CODYAI_STATE_DIR}/openclaw.json"

echo "==> Build"
pnpm build

echo "==> Seed state"
mkdir -p "${CODYAI_STATE_DIR}/credentials"
mkdir -p "${CODYAI_STATE_DIR}/agents/main/sessions"
echo '{}' >"${CODYAI_CONFIG_PATH}"
echo 'creds' >"${CODYAI_STATE_DIR}/credentials/marker.txt"
echo 'session' >"${CODYAI_STATE_DIR}/agents/main/sessions/sessions.json"

echo "==> Reset (config+creds+sessions)"
pnpm openclaw reset --scope config+creds+sessions --yes --non-interactive

test ! -f "${CODYAI_CONFIG_PATH}"
test ! -d "${CODYAI_STATE_DIR}/credentials"
test ! -d "${CODYAI_STATE_DIR}/agents/main/sessions"

echo "==> Recreate minimal config"
mkdir -p "${CODYAI_STATE_DIR}/credentials"
echo '{}' >"${CODYAI_CONFIG_PATH}"

echo "==> Uninstall (state only)"
pnpm openclaw uninstall --state --yes --non-interactive

test ! -d "${CODYAI_STATE_DIR}"

echo "OK"
