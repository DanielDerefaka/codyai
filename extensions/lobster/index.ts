import type {
  AnyAgentTool,
  CodyAIPluginApi,
  CodyAIPluginToolFactory,
} from "openclaw/plugin-sdk/lobster";
import { createLobsterTool } from "./src/lobster-tool.js";

export default function register(api: CodyAIPluginApi) {
  api.registerTool(
    ((ctx) => {
      if (ctx.sandboxed) {
        return null;
      }
      return createLobsterTool(api) as AnyAgentTool;
    }) as CodyAIPluginToolFactory,
    { optional: true },
  );
}
