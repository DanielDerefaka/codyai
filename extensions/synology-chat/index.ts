import type { CodyAIPluginApi } from "openclaw/plugin-sdk/synology-chat";
import { emptyPluginConfigSchema } from "openclaw/plugin-sdk/synology-chat";
import { createSynologyChatPlugin } from "./src/channel.js";
import { setSynologyRuntime } from "./src/runtime.js";

const plugin = {
  id: "synology-chat",
  name: "Synology Chat",
  description: "Native Synology Chat channel plugin for CodyAI",
  configSchema: emptyPluginConfigSchema(),
  register(api: CodyAIPluginApi) {
    setSynologyRuntime(api.runtime);
    api.registerChannel({ plugin: createSynologyChatPlugin() });
  },
};

export default plugin;
