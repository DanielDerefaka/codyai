// Narrow plugin-sdk surface for the bundled diffs plugin.
// Keep this list additive and scoped to symbols used under extensions/diffs.

export type { CodyAIConfig } from "../config/config.js";
export { resolvePreferredCodyAITmpDir } from "../infra/tmp-openclaw-dir.js";
export type {
  AnyAgentTool,
  CodyAIPluginApi,
  CodyAIPluginConfigSchema,
  PluginLogger,
} from "../plugins/types.js";
