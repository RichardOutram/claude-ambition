// The bench's permission host for plan-mode examples: a tiny MCP server (stdio, no dependencies) passed to
// `claude -p` as --permission-prompt-tool. Headless Claude only offers ExitPlanMode, the plan approval step,
// when something can answer permission prompts. This answers them the way the bench's VM user does, the same
// for every arm:
// - ExitPlanMode: approve the plan, as a user does after the first pass. Claude leaves plan mode.
// - File edits that reach here (plan mode sends edits to the host even when allowed): only Claude's own plan
//   file, as plan mode allows interactively. After approval, edits in the workspace are accepted by the mode.
// - Everything else: allow. Inside the VM every command is allowed; the VM is the boundary.
import readline from "node:readline";

const EDITS = new Set(["Write", "Edit", "MultiEdit", "NotebookEdit"]);
const PLANS = (process.env.CLAUDE_CONFIG_DIR || "/cfg") + "/plans/";

function decide(tool, input) {
  if (EDITS.has(tool)) {
    const file = String(input.file_path || input.notebook_path || "");
    if (!file.startsWith(PLANS))
      return { behavior: "deny", message: "Plan mode is on: no file edits until the plan is approved." };
  }
  return { behavior: "allow", updatedInput: input };
}

const send = (msg) => process.stdout.write(JSON.stringify({ jsonrpc: "2.0", ...msg }) + "\n");

readline.createInterface({ input: process.stdin }).on("line", (line) => {
  let req;
  try { req = JSON.parse(line); } catch { return; }
  if (req.id === undefined) return; // notifications
  if (req.method === "initialize")
    return send({ id: req.id, result: { protocolVersion: req.params?.protocolVersion || "2025-06-18",
      capabilities: { tools: {} }, serverInfo: { name: "bench", version: "1" } } });
  if (req.method === "tools/list")
    return send({ id: req.id, result: { tools: [{ name: "approve", description: "Answers permission prompts for the bench.",
      inputSchema: { type: "object", properties: { tool_name: { type: "string" }, input: { type: "object" },
        tool_use_id: { type: "string" } }, required: ["tool_name", "input"] } }] } });
  if (req.method === "tools/call") {
    const { tool_name, input = {} } = req.params?.arguments || {};
    return send({ id: req.id, result: { content: [{ type: "text", text: JSON.stringify(decide(tool_name, input)) }] } });
  }
  if (req.method === "ping") return send({ id: req.id, result: {} });
  send({ id: req.id, error: { code: -32601, message: `unknown method ${req.method}` } });
});
