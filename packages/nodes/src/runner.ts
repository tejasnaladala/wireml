/**
 * Runtime-agnostic execution contract. Both WebGraphRunner (browser) and
 * LocalGraphRunner (FastAPI client) implement this interface. The scheduler
 * in the UI chooses which runner to use per-node based on capability.
 */

import type { GraphJSON, NodeInstance, RuntimeCapabilities } from './schema.js';

export type NodeIO = Record<string, unknown>;

export interface NodeExecutionContext {
  /** Inputs produced by upstream nodes. */
  inputs: NodeIO;
  /** Signal used to cancel long-running executions. */
  signal?: AbortSignal;
  /** Progress reporter for long-running nodes (model download, training). */
  onProgress?: (fraction: number, message?: string) => void;
  /** Access to the graph so context-aware nodes can look up siblings. */
  graph: GraphJSON;
}

export interface NodeExecutionResult {
  outputs: NodeIO;
  /** Error state — bubbles into the node UI. */
  error?: { message: string; stack?: string };
}

export interface GraphRunner {
  kind: 'web' | 'local';
  capabilities(): Promise<RuntimeCapabilities>;
  runNode(node: NodeInstance, ctx: NodeExecutionContext): Promise<NodeExecutionResult>;
  /** Optional: whole-graph execution (some runners can batch). */
  runGraph?(graph: GraphJSON, signal?: AbortSignal): AsyncIterable<{
    nodeId: string;
    result: NodeExecutionResult;
  }>;
}

/** Topologically sort a graph's nodes so each is executed after its upstreams. */
export function topoSort(graph: GraphJSON): NodeInstance[] {
  const byId = new Map(graph.nodes.map((n) => [n.id, n] as const));
  const incoming = new Map<string, Set<string>>();
  graph.nodes.forEach((n) => incoming.set(n.id, new Set()));
  graph.edges.forEach((e) => {
    incoming.get(e.target.nodeId)!.add(e.source.nodeId);
  });

  const ready = graph.nodes.filter((n) => incoming.get(n.id)!.size === 0);
  const sorted: NodeInstance[] = [];
  while (ready.length > 0) {
    const n = ready.shift()!;
    sorted.push(n);
    graph.edges.forEach((e) => {
      if (e.source.nodeId === n.id) {
        const deps = incoming.get(e.target.nodeId)!;
        deps.delete(n.id);
        if (deps.size === 0) {
          const target = byId.get(e.target.nodeId);
          if (target && !sorted.includes(target)) ready.push(target);
        }
      }
    });
  }
  if (sorted.length !== graph.nodes.length) {
    throw new Error('Graph contains a cycle');
  }
  return sorted;
}
