/**
 * Client for the local Python runtime. Proxies every node execution to the
 * FastAPI service at /runtime/runNode. The server-side implementation lives
 * in apps/runtime/.
 */

import type {
  GraphRunner,
  NodeExecutionContext,
  NodeExecutionResult,
  NodeInstance,
  RuntimeCapabilities,
} from '@wireml/nodes';

export class LocalGraphRunner implements GraphRunner {
  readonly kind = 'local' as const;

  constructor(private readonly baseUrl = '/runtime') {}

  async capabilities(): Promise<RuntimeCapabilities> {
    const res = await fetch(`${this.baseUrl}/capabilities`);
    if (!res.ok) throw new Error(`Failed to read local runtime capabilities: ${res.status}`);
    return (await res.json()) as RuntimeCapabilities;
  }

  async runNode(node: NodeInstance, ctx: NodeExecutionContext): Promise<NodeExecutionResult> {
    const res = await fetch(`${this.baseUrl}/runNode`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        node,
        inputs: serializeInputs(ctx.inputs),
      }),
      signal: ctx.signal,
    });
    if (!res.ok) {
      return {
        outputs: {},
        error: { message: `Local runtime error: ${res.status} ${res.statusText}` },
      };
    }
    return (await res.json()) as NodeExecutionResult;
  }
}

/**
 * Transport-friendly serialization. Images and audio get base64-encoded;
 * everything else is passed as-is.
 */
function serializeInputs(inputs: Record<string, unknown>): Record<string, unknown> {
  const out: Record<string, unknown> = {};
  for (const [k, v] of Object.entries(inputs)) {
    if (v instanceof Blob) {
      out[k] = { __blob: true, mime: v.type, size: v.size };
    } else {
      out[k] = v;
    }
  }
  return out;
}
