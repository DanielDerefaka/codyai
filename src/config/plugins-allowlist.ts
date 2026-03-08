import type { CodyAIConfig } from "./config.js";

export function ensurePluginAllowlisted(cfg: CodyAIConfig, pluginId: string): CodyAIConfig {
  const allow = cfg.plugins?.allow;
  if (!Array.isArray(allow) || allow.includes(pluginId)) {
    return cfg;
  }
  return {
    ...cfg,
    plugins: {
      ...cfg.plugins,
      allow: [...allow, pluginId],
    },
  };
}
