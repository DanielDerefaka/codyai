import type { CodyAIPluginApi } from "openclaw/plugin-sdk/googlechat";
import { emptyPluginConfigSchema } from "openclaw/plugin-sdk/googlechat";
import { googlechatDock, googlechatPlugin } from "./src/channel.js";
import { setGoogleChatRuntime } from "./src/runtime.js";

const plugin = {
  id: "googlechat",
  name: "Google Chat",
  description: "CodyAI Google Chat channel plugin",
  configSchema: emptyPluginConfigSchema(),
  register(api: CodyAIPluginApi) {
    setGoogleChatRuntime(api.runtime);
    api.registerChannel({ plugin: googlechatPlugin, dock: googlechatDock });
  },
};

export default plugin;
